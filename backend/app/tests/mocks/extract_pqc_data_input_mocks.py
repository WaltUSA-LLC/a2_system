import pandas as pd

"""
mimic data output of extract_base_data (db) in _extract_pqc_data (pqc raw data)
"""

RAW_PQC_COLUMNS = [
    "Date",
    "Shift",
    "Role_Name",
    "DateRec",
    "MachID",
    "Style_Code",
    "toeHole",
    "brokenNDL",
    "missNDL",
    "fanYarn",
    "missYarn",
    "logoIssue",
    "dirty",
    "feisha",
    "other",
]


def make_empty_raw_pqc_df() -> pd.DataFrame:
    return pd.DataFrame(columns=RAW_PQC_COLUMNS)


def make_base_raw_pqc_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Date": ["2026-05-01", "2026-05-01", "2026-05-01"],
            "Shift": ["07:00:00", "07:00:00", "07:00:00"],
            "Role_Name": ["KO - Alice", "Tech - Bob", "KO - Alice"],
            "DateRec": pd.to_datetime(
                [
                    "2026-05-01 07:10:00",
                    "2026-05-01 07:20:00",
                    "2026-05-01 07:35:00",
                ]
            ),
            "MachID": ["M1", "M2", "M1"],
            "Style_Code": [" abc red ", "ABC blue", "abc red"],
            "toeHole": [1, 0, 1],
            "brokenNDL": [0, 1, 0],
            "missNDL": [0, 0, 1],
            "fanYarn": [0, 0, 0],
            "missYarn": [0, 1, 0],
            "logoIssue": [0, 0, 0],
            "dirty": [0, 0, 0],
            "feisha": [0, 0, 0],
            "other": [0, 0, 0],
        }
    )


def make_multi_shift_raw_pqc_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Date": [
                "2026-05-01",
                "2026-05-01",
                "2026-05-01",
                "2026-05-02",
            ],
            "Shift": ["07:00:00", "07:00:00", "19:00:00", "07:00:00"],
            "Role_Name": ["KO - Alice", "Tech - Bob", "KO - Cara", "Tech - Dan"],
            "DateRec": pd.to_datetime(
                [
                    "2026-05-01 07:10:00",
                    "2026-05-01 07:20:00",
                    "2026-05-01 19:15:00",
                    "2026-05-02 07:25:00",
                ]
            ),
            "MachID": ["M1", "M2", "M3", "M4"],
            "Style_Code": ["abc red", "ABC blue", "xyz black", "qwe white"],
            "toeHole": [2, 0, 2, 0],
            "brokenNDL": [0, 1, 0, 2],
            "missNDL": [0, 1, 0, 0],
            "fanYarn": [0, 0, 0, 0],
            "missYarn": [0, 0, 0, 0],
            "logoIssue": [0, 0, 0, 0],
            "dirty": [0, 0, 2, 0],
            "feisha": [0, 0, 0, 0],
            "other": [0, 0, 0, 1],
        }
    )


def make_raw_pqc_staff_detail_df_with_invalid_values() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Date": ["2026-05-01", "2026-05-01"],
            "Shift": ["07:00:00", "07:00:00"],
            "Role_Name": ["KO - Alice", "KO - Alice"],
            "DateRec": pd.to_datetime(
                [
                    "2026-05-01 07:20:00",
                    "2026-05-01 07:10:00",
                ]
            ),
            "MachID": ["M1", "M2"],
            "Style_Code": [" abc red ", "XYZ black "],
            "toeHole": [1, 0],
            "brokenNDL": [float("nan"), 0],
            "missNDL": [0, float("inf")],
            "fanYarn": [0, 0],
            "missYarn": [0, 0],
            "logoIssue": [0, 0],
            "dirty": [float("-inf"), 0],
            "feisha": [0, 0],
            "other": [0, 0],
        }
    )


def make_raw_pqc_df_with_invalid_style_code() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Date": ["2026-05-01", "2026-05-01", "2026-05-01"],
            "Shift": ["07:00:00", "07:00:00", "07:00:00"],
            "Role_Name": ["KO - Alice", "Tech - Bob", "KO - Cara"],
            "DateRec": pd.to_datetime(
                [
                    "2026-05-01 07:10:00",
                    "2026-05-01 07:20:00",
                    "2026-05-01 07:30:00",
                ]
            ),
            "MachID": ["M1", "M2", "M3"],
            "Style_Code": ["", "   ", None],
            "toeHole": [1, 1, 1],
            "brokenNDL": [0, 0, 0],
            "missNDL": [0, 0, 0],
            "fanYarn": [0, 0, 0],
            "missYarn": [0, 0, 0],
            "logoIssue": [0, 0, 0],
            "dirty": [0, 0, 0],
            "feisha": [0, 0, 0],
            "other": [0, 0, 0],
        }
    )
