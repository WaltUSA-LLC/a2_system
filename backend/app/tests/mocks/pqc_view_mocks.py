import pandas as pd


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
            "Style_Code": ["abc red", "abc red", "ABC blue", "xyz black"],
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
            "Style_Code": ["abc red", "abc red", "ABC blue", "abc green"],
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
