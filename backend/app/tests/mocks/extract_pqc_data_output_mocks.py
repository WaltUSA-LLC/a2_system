import pandas as pd

"""
mimic data output of _extract_pqc_data
"""

def make_base_pqc_shift_df():
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Shift_Start_Time": [shift_time, shift_time],
            "MachID": ["M1", "M2"],
            "Style_Code": ["abc red", "ABC blue"],
            "toeHole": [1, 0],
            "brokenNDL": [1, 0],
            "missNDL": [0, 1],
            "fanYarn": [0, 0],
            "missYarn": [1, 0],
            "logoIssue": [0, 0],
            "dirty": [0, 0],
            "feisha": [0, 0],
            "other": [0, 0],
        }
    )


def make_multi_pqc_shift_df():
    shift_1 = pd.Timestamp("2026-05-01 07:00:00")
    shift_2 = pd.Timestamp("2026-05-01 19:00:00")

    return pd.DataFrame(
        {
            "Shift_Start_Time": [
                shift_1,
                shift_1,
                shift_2,
                shift_2,
                shift_2,
            ],
            "MachID": ["M1", "M2", "M3", "M4", "M5"],
            "Style_Code": [
                "abc red",
                "ABC blue",
                "xyz black",
                "qwe white",
                "xyz black",
            ],
            "toeHole": [2, 0, 2, 0, 0],
            "brokenNDL": [0, 1, 0, 2, 0],
            "missNDL": [0, 1, 0, 0, 0],
            "fanYarn": [0, 0, 0, 0, 0],
            "missYarn": [0, 0, 0, 0, 0],
            "logoIssue": [0, 0, 0, 0, 0],
            "dirty": [0, 0, 0, 0, 2],
            "feisha": [0, 0, 0, 0, 0],
            "other": [0, 0, 0, 0, 0],
        }
    )


def make_base_pqc_mach_detail_df():
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Shift_Start_Time": [shift_time, shift_time, shift_time, shift_time],
            "MachID": ["M1", "M1", "M2", "M3"],
            "Style_Code": ["ABC RED", "ABC RED", "ABC BLUE", "XYZ BLACK"],
            "toeHole": [1, 1, 0, 0],
            "brokenNDL": [1, 0, 1, 0],
            "missNDL": [0, 1, 1, 0],
            "fanYarn": [0, 0, 0, 0],
            "missYarn": [0, 0, 0, 0],
            "logoIssue": [0, 0, 0, 0],
            "dirty": [0, 0, 0, 0],
            "feisha": [0, 0, 0, 0],
            "other": [0, 0, 0, 0],
        }
    )


def make_metrics_pqc_mach_detail_df():
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Shift_Start_Time": [shift_time, shift_time, shift_time, shift_time],
            "MachID": ["M_GOOD", "M_GOOD", "M_BOUNDARY", "M_LOW"],
            "Style_Code": ["ABC RED", "ABC RED", "ABC BLUE", "ABC GREEN"],
            "toeHole": [1, 1, 0, 1],
            "brokenNDL": [1, 0, 1, 1],
            "missNDL": [0, 1, 1, 1],
            "fanYarn": [0, 0, 0, 1],
            "missYarn": [0, 0, 0, 1],
            "logoIssue": [0, 0, 0, 1],
            "dirty": [0, 0, 0, 0],
            "feisha": [0, 0, 0, 0],
            "other": [0, 0, 0, 0],
        }
    )


def make_base_pqc_sku_mach_detail_df():
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Shift_Start_Time": [shift_time, shift_time, shift_time, shift_time],
            "MachID": ["M1", "M2", "M2", "M3"],
            "Style_Code": ["ABC BLUE", "ABC RED", "ABC RED", "XYZ BLACK"],
            "toeHole": [0, 1, 1, 0],
            "brokenNDL": [1, 1, 0, 0],
            "missNDL": [1, 0, 1, 0],
            "fanYarn": [0, 0, 0, 0],
            "missYarn": [0, 0, 0, 0],
            "logoIssue": [0, 0, 0, 0],
            "dirty": [0, 0, 0, 0],
            "feisha": [0, 0, 0, 0],
            "other": [0, 0, 0, 0],
        }
    )


def make_metrics_pqc_sku_mach_detail_df():
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Shift_Start_Time": [shift_time, shift_time, shift_time, shift_time],
            "MachID": ["M1", "M1", "M2", "M3"],
            "Style_Code": ["ABC RED", "ABC RED", "ABC BLUE", "ABC GREEN"],
            "toeHole": [1, 1, 0, 1],
            "brokenNDL": [1, 0, 1, 1],
            "missNDL": [0, 1, 1, 1],
            "fanYarn": [0, 0, 0, 1],
            "missYarn": [0, 0, 0, 1],
            "logoIssue": [0, 0, 0, 1],
            "dirty": [0, 0, 0, 0],
            "feisha": [0, 0, 0, 0],
            "other": [0, 0, 0, 0],
        }
    )


def make_base_pqc_staff_df():
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Shift_Start_Time": [
                shift_time,
                shift_time,
                shift_time,
                shift_time,
            ],
            "DateRec": pd.to_datetime(
                [
                    "2026-05-01 07:40:00",
                    "2026-05-01 07:20:00",
                    "2026-05-01 07:10:00",
                    "2026-05-01 07:30:00",
                ]
            ),
            "MachID": ["M1", "M2", "M3", "M4"],
            "Style_Code": ["ABC RED", "ABC BLUE", "ABC RED", "XYZ BLACK"],
            "Role": ["KO", "Tech", "KO", "Tech"],
            "Name": ["Alice", "Bob", "Alice", "Alice"],
            "toeHole": [0, 0, 1, 0],
            "brokenNDL": [1, 0, 0, 0],
            "missNDL": [1, 0, 0, 0],
            "fanYarn": [0, 0, 0, 1],
            "missYarn": [0, 0, 1, 0],
            "logoIssue": [0, 0, 0, 0],
            "dirty": [0, 1, 0, 0],
            "feisha": [0, 0, 0, 0],
            "other": [0, 0, 0, 1],
        }
    )


def make_pqc_staff_df_with_threshold_intervals():
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Shift_Start_Time": [
                shift_time,
                shift_time,
                shift_time,
                shift_time,
                shift_time,
            ],
            "DateRec": pd.to_datetime(
                [
                    "2026-05-01 08:30:00",
                    "2026-05-01 07:55:00",
                    "2026-05-01 07:30:00",
                    "2026-05-01 07:10:00",
                    "2026-05-01 07:45:00",
                ]
            ),
            "MachID": ["M1", "M2", "M3", "M4", "M5"],
            "Style_Code": [
                "ABC RED",
                "ABC BLUE",
                "ABC GREEN",
                "ABC BLACK",
                "XYZ BLACK",
            ],
            "Role": ["KO", "KO", "KO", "KO", "Tech"],
            "Name": ["Alice", "Alice", "Alice", "Alice", "Bob"],
            "toeHole": [0, 1, 0, 1, 0],
            "brokenNDL": [0, 0, 1, 0, 0],
            "missNDL": [1, 0, 0, 0, 0],
            "fanYarn": [0, 0, 0, 0, 0],
            "missYarn": [0, 0, 0, 1, 0],
            "logoIssue": [0, 0, 0, 0, 0],
            "dirty": [0, 0, 0, 0, 1],
            "feisha": [0, 0, 0, 0, 0],
            "other": [0, 0, 0, 0, 0],
        }
    )


def make_multi_pqc_staff_shift_df():
    df = make_base_pqc_staff_df()
    night_shift_row = df.iloc[[2]].copy()
    night_shift_row["Shift_Start_Time"] = pd.Timestamp("2026-05-01 19:00:00")
    night_shift_row["DateRec"] = pd.Timestamp("2026-05-01 19:15:00")
    night_shift_row["MachID"] = "M5"

    return pd.concat([night_shift_row, df], ignore_index=True)


def make_pqc_staff_detail_df_with_invalid_values():
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Shift_Start_Time": [shift_time, shift_time],
            "DateRec": pd.to_datetime(
                [
                    "2026-05-01 07:20:00",
                    "2026-05-01 07:10:00",
                ]
            ),
            "MachID": ["M1", "M2"],
            "Style_Code": [" ABC RED ", "XYZ BLACK "],
            "Role": ["KO", "KO"],
            "Name": ["Alice", "Alice"],
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
