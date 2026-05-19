import os
from datetime import datetime, time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


EXCEL_PATH = Path(__file__).with_name("schedule.xlsx")
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"


ROLE_MAP = {
    "Knitting operator": "KO",
    "Technician": "Tech",
    "Creeler": "Creeler",
    "Yarn Prep": "Yarner",
}

MONTH={1:"Jan", 2:"Feb", 3:"Mar", 4:"April", 5:"May",\
       6:"Jun", 7:"Jul", 8:"Aug", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dec"}

def clear_knit_schedule(
    year: int,
    month: int,
    database_url: str | None = None,
    engine: Engine | None = None,
) -> int:
    """
    Delete ShiftOperator rows for one calendar month.

    The month range is inclusive at the start and exclusive at the next month,
    so it works for months with 28, 29, 30, or 31 days.
    """
    if month < 1 or month > 12:
        raise ValueError("month must be between 1 and 12")

    month_start = datetime(year, month, 1)
    if month == 12:
        next_month_start = datetime(year + 1, 1, 1)
    else:
        next_month_start = datetime(year, month + 1, 1)

    owns_engine = engine is None
    if engine is None:
        load_dotenv(ENV_PATH)
        resolved_database_url = database_url or os.getenv("DATABASE_URL")
        if not resolved_database_url:
            raise ValueError("DATABASE_URL is missing. Set it in .env or pass database_url.")
        engine = create_engine(resolved_database_url)

    delete_stmt = text(
        """
        DELETE FROM dbA2.dbo.ShiftOperator
        WHERE ShiftStartTime >= :month_start
          AND ShiftStartTime < :next_month_start
        """
    )

    try:
        with engine.begin() as conn:
            result = conn.execute(
                delete_stmt,
                {
                    "month_start": month_start,
                    "next_month_start": next_month_start,
                },
            )
        if result.rowcount is None or result.rowcount < 0:
            return 0
        return result.rowcount
    finally:
        if owns_engine:
            engine.dispose()


def parse_knit_schedule_excel(excel_path: str | Path, sheet_name: str) -> pd.DataFrame:
    """
    Parse schedule Excel sheet into long format:
    ShiftStartTime | OperatorID
    """
    df = pd.read_excel(
        excel_path,
        sheet_name=sheet_name,
        header=None,
    )

    # the first three lines are headers
    role_row = df.iloc[0].ffill()
    name_row = df.iloc[1]
    id_row = df.iloc[2]

    # true data for schedule
    data = df.iloc[3:].copy()
    data.iloc[:, 0] = data.iloc[:, 0].ffill()

    records = []
    current_date = None

    for _, row in data.iterrows():
        raw_date = row.iloc[0]       # Date column
        shift_type = row.iloc[2]     # Day / Night column

        if pd.notna(raw_date):
            current_date = pd.to_datetime(raw_date).date()

        if current_date is None:
            continue

        if pd.isna(shift_type):
            continue

        shift_type = str(shift_type).strip()

        if shift_type == "Day":
            shift_start_time = datetime.combine(current_date, time(7, 0, 0))
        elif shift_type == "Night":
            shift_start_time = datetime.combine(current_date, time(19, 0, 0))
        else:
            continue

        # the first three are Date / week / Shift separately
        for col_idx in range(3, df.shape[1]):
            role_raw = role_row.iloc[col_idx]
            operator_name_raw = name_row.iloc[col_idx]
            operator_id_raw = id_row.iloc[col_idx]

            # ignore for role
            if pd.isna(role_raw):
                continue
            role_raw = str(role_raw).strip()
            if role_raw not in ROLE_MAP:
                continue

            # ignore TIME/TTL for name
            if pd.notna(operator_name_raw):
                operator_name = str(operator_name_raw).strip()
                if operator_name.upper() in {"TIME", "TTL"}:
                    continue

            # must have OperatorID
            if pd.isna(operator_id_raw):
                continue
            try:
                operator_id = int(operator_id_raw)
            except ValueError:
                continue

            cell_value = row.iloc[col_idx]
            if pd.notna(cell_value) and cell_value == 1:
                records.append(
                    {
                        "ShiftStartTime": shift_start_time,
                        "OperatorID": operator_id,
                        "RoleName": ROLE_MAP[role_raw],
                    }
                )

    result = pd.DataFrame(records, columns=["ShiftStartTime", "OperatorID", "RoleName"])

    result = result.drop_duplicates(
        subset=["ShiftStartTime", "OperatorID"]
    ).reset_index(drop=True)

    return result


def write_shift_operators_to_db(
    schedule_df: pd.DataFrame,
    database_url: str | None = None,
    engine: Engine | None = None,
) -> int:
    """
    Write parsed schedule rows into ShiftOperator.

    Existing (ShiftStartTime, OperatorID) rows are skipped so this can be
    safely rerun for the same spreadsheet.
    """
    required_columns = {"ShiftStartTime", "OperatorID", "RoleName"}
    missing_columns = required_columns - set(schedule_df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"schedule_df is missing required columns: {missing}")

    records_df = (
        schedule_df.loc[:, ["ShiftStartTime", "OperatorID", "RoleName"]]
        .dropna()
        .drop_duplicates(subset=["ShiftStartTime", "OperatorID", "RoleName"])
    )
    if records_df.empty:
        return 0

    records = [
        {
            "shift_start_time": pd.to_datetime(row.ShiftStartTime).to_pydatetime(),
            "operator_id": int(row.OperatorID),
            "role_name": str(row.RoleName),
        }
        for row in records_df.itertuples(index=False)
    ]

    owns_engine = engine is None
    if engine is None:
        load_dotenv(ENV_PATH)
        resolved_database_url = database_url or os.getenv("DATABASE_URL")
        if not resolved_database_url:
            raise ValueError("DATABASE_URL is missing. Set it in .env or pass database_url.")
        engine = create_engine(resolved_database_url)

    insert_stmt = text(
        """
        INSERT INTO dbA2.dbo.ShiftOperator (ShiftStartTime, OperatorID, RoleName)
        SELECT :shift_start_time, :operator_id, :role_name
        WHERE NOT EXISTS (
            SELECT 1
            FROM dbA2.dbo.ShiftOperator
            WHERE ShiftStartTime = :shift_start_time
              AND OperatorID = :operator_id
              AND RoleName = :role_name
        )
        """
    )

    try:
        with engine.begin() as conn:
            result = conn.execute(insert_stmt, records)
        if result.rowcount is None or result.rowcount < 0:
            return len(records)
        return result.rowcount
    finally:
        if owns_engine:
            engine.dispose()


if __name__ == "__main__":
    year = 2026
    for month in range(1,6):
        clear_knit_schedule(year, month)
        schedule_df = parse_knit_schedule_excel(EXCEL_PATH, MONTH[month])
        inserted_count = write_shift_operators_to_db(schedule_df)
        print(f"{year}-{month}: Total parsed records: {len(schedule_df)}")
        print(f"{year}-{month}: Inserted records: {inserted_count}")
