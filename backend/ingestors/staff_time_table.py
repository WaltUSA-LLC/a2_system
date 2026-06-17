import os
import logging
from datetime import datetime, time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection


EXCEL_PATH = Path(__file__).with_name("schedule.xlsx")
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
logger = logging.getLogger(__name__)


ROLE_MAP = {
    "Knitting operator": "KO",
    "Technician": "Tech",
    "Creeler": "Creeler",
    "Yarn Prep": "Yarner",
}

MONTH={1:"Jan", 2:"Feb", 3:"Mar", 4:"April", 5:"May",\
       6:"Jun", 7:"Jul", 8:"Aug", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dec"}


def _month_range(year: int, month: int) -> tuple[datetime, datetime]:
    if month < 1 or month > 12:
        raise ValueError("month must be between 1 and 12")

    month_start = datetime(year, month, 1)
    if month == 12:
        next_month_start = datetime(year + 1, 1, 1)
    else:
        next_month_start = datetime(year, month + 1, 1)

    return month_start, next_month_start


def _clear_knit_schedule(
    conn: Connection,
    month_start: datetime,
    next_month_start: datetime,
) -> int:
    """
    Delete ShiftOperator rows for one calendar month.

    The month range is inclusive at the start and exclusive at the next month,
    so it works for months with 28, 29, 30, or 31 days.
    """
    delete_stmt = text(
        """
        DELETE FROM dbA2.dbo.ShiftOperator
        WHERE ShiftStartTime >= :month_start
          AND ShiftStartTime < :next_month_start
        """
    )

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


def _parse_knit_schedule_excel(excel_path: str | Path, sheet_name: str) -> pd.DataFrame:
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

    for row_idx, row in data.iterrows():
        excel_row = row_idx + 1
        raw_date = row.iloc[0]       # Date column
        shift_type = row.iloc[2]     # Day / Night column

        if pd.notna(raw_date):
            current_date = pd.to_datetime(raw_date).date()

        if current_date is None:
            raise ValueError(f"missing schedule date at row {excel_row}")

        if pd.isna(shift_type):
            raise ValueError(f"missing shift type at row {excel_row}")

        shift_type = str(shift_type).strip()

        if shift_type == "Day":
            shift_start_time = datetime.combine(current_date, time(7, 0, 0))
        elif shift_type == "Night":
            shift_start_time = datetime.combine(current_date, time(19, 0, 0))
        else:
            logger.warning(
                "Skipping sheet %s row %s: unsupported shift type %r.",
                sheet_name,
                excel_row,
                shift_type,
            )
            continue

        # the first three are Date / week / Shift separately
        for col_idx in range(3, df.shape[1]):
            excel_col = col_idx + 1
            role_raw = role_row.iloc[col_idx]
            operator_name_raw = name_row.iloc[col_idx]
            operator_id_raw = id_row.iloc[col_idx]

            # ignore for role
            if pd.isna(role_raw):
                raise ValueError(f"missing role header at col {excel_col}")
                
            role_raw = str(role_raw).strip()
            if role_raw not in ROLE_MAP:
                raise ValueError(f"unsupported role header {role_raw} at col {excel_col}")
            # ignore TIME/TTL for name
            if pd.notna(operator_name_raw):
                operator_name = str(operator_name_raw).strip()
                if operator_name.upper() in {"TIME", "TTL"}:
                    continue

            # must have OperatorID
            if pd.isna(operator_id_raw):
                raise ValueError(f"no operator id header at col {excel_col}")
            try:
                operator_id = int(operator_id_raw)
            except ValueError:
                raise ValueError(f"operator id invalid at col {excel_col}")

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


def write_staff_schedule_to_db(
    year: int,
    month: int,
    excel_path: str | Path = EXCEL_PATH,
) -> int:
    """
    Write one month of parsed schedule rows into ShiftOperator.

    Existing rows for the month are cleared before writing the parsed rows.
    """
    month_start, next_month_start = _month_range(year, month)
    schedule_df = _parse_knit_schedule_excel(excel_path, MONTH[month])

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

    records = [
        {
            "shift_start_time": pd.to_datetime(row.ShiftStartTime).to_pydatetime(),
            "operator_id": int(row.OperatorID),
            "role_name": str(row.RoleName),
        }
        for row in records_df.itertuples(index=False)
    ]

    load_dotenv(ENV_PATH)
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL is missing. Set it in .env.")
    engine = create_engine(database_url)

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
            _clear_knit_schedule(conn, month_start, next_month_start)
            if not records:
                return 0
            result = conn.execute(insert_stmt, records)
        if result.rowcount is None or result.rowcount < 0:
            return len(records)
        return result.rowcount
    finally:
        engine.dispose()


if __name__ == "__main__":
    year = 2026
    for month in range(1,3):
        inserted_count = write_staff_schedule_to_db(year, month)
        print(f"{year}-{month}: Inserted records: {inserted_count}")
