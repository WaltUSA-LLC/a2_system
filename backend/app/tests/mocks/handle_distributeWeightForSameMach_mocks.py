import pandas as pd


def make_single_row_same_mach_df() -> pd.DataFrame:
    shift_time = pd.Timestamp("2026-05-01 08:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["abc red"],
            "Shift_Start_Time": [shift_time],
            "MachID": ["M1"],
            "ON_Time": [50],
            "OFF_Time": [10],
            "Avg_Cycle": [10],
            "Weight": [100],
            "Prs_Weight": [1000],
            "NAU_prs": [10],
            "Discard_prs": [0],
        }
    )


def make_same_mach_same_shift_df() -> pd.DataFrame:
    shift_time = pd.Timestamp("2026-05-01 08:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["abc red", "abc blue"],
            "Shift_Start_Time": [shift_time, shift_time],
            "MachID": ["M1", "M1"],
            "ON_Time": [30, 70],
            "OFF_Time": [10, 20],
            "Avg_Cycle": [10, 10],
            "Weight": [100, 100],
            "Prs_Weight": [1000, 1000],
            "NAU_prs": [3, 7],
            "Discard_prs": [0, 0],
        }
    )


def make_different_mach_same_shift_df() -> pd.DataFrame:
    shift_time = pd.Timestamp("2026-05-01 08:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["abc red", "abc blue", "xyz black", "xyz white"],
            "Shift_Start_Time": [
                shift_time,
                shift_time,
                shift_time,
                shift_time,
            ],
            "MachID": ["M1", "M1", "M2", "M2"],
            "ON_Time": [30, 70, 20, 80],
            "OFF_Time": [10, 20, 15, 25],
            "Avg_Cycle": [10, 10, 10, 10],
            "Weight": [100, 100, 200, 200],
            "Prs_Weight": [1000, 1000, 1000, 1000],
            "NAU_prs": [3, 7, 4, 16],
            "Discard_prs": [0, 0, 0, 0],
        }
    )


def make_same_mach_different_shift_df() -> pd.DataFrame:
    shift_1 = pd.Timestamp("2026-05-01 08:00:00")
    shift_2 = pd.Timestamp("2026-05-01 20:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["abc red", "abc blue", "abc green", "abc black"],
            "Shift_Start_Time": [shift_1, shift_1, shift_2, shift_2],
            "MachID": ["M1", "M1", "M1", "M1"],
            "ON_Time": [25, 75, 40, 60],
            "OFF_Time": [10, 20, 15, 25],
            "Avg_Cycle": [10, 10, 10, 10],
            "Weight": [100, 100, 300, 300],
            "Prs_Weight": [1000, 1000, 1000, 1000],
            "NAU_prs": [2, 8, 12, 18],
            "Discard_prs": [0, 0, 0, 0],
        }
    )


def make_zero_on_time_same_mach_df() -> pd.DataFrame:
    shift_time = pd.Timestamp("2026-05-01 08:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["abc red", "abc blue"],
            "Shift_Start_Time": [shift_time, shift_time],
            "MachID": ["M1", "M1"],
            "ON_Time": [0, 0],
            "OFF_Time": [50, 50],
            "Avg_Cycle": [10, 10],
            "Weight": [100, 100],
            "Prs_Weight": [1000, 1000],
            "NAU_prs": [0, 0],
            "Discard_prs": [0, 0],
        }
    )


def make_mixed_zero_and_nonzero_on_time_df() -> pd.DataFrame:
    shift_time = pd.Timestamp("2026-05-01 08:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["abc red", "abc blue"],
            "Shift_Start_Time": [shift_time, shift_time],
            "MachID": ["M1", "M1"],
            "ON_Time": [0, 100],
            "OFF_Time": [50, 0],
            "Avg_Cycle": [10, 10],
            "Weight": [100, 100],
            "Prs_Weight": [1000, 1000],
            "NAU_prs": [0, 10],
            "Discard_prs": [0, 0],
        }
    )


def make_same_mach_df_with_extra_columns() -> pd.DataFrame:
    shift_time = pd.Timestamp("2026-05-01 08:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["abc red", "abc blue"],
            "Shift_Start_Time": [shift_time, shift_time],
            "MachID": ["M1", "M1"],
            "ON_Time": [40, 60],
            "OFF_Time": [10, 20],
            "Avg_Cycle": [10, 10],
            "Weight": [100, 100],
            "Prs_Weight": [1000, 1000],
            "NAU_prs": [4, 6],
            "Discard_prs": [0, 0],
            "Comment": ["keep first", "keep second"],
        }
    )


def make_same_mach_df_with_unexpected_different_weights() -> pd.DataFrame:
    shift_time = pd.Timestamp("2026-05-01 08:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["abc red", "abc blue"],
            "Shift_Start_Time": [shift_time, shift_time],
            "MachID": ["M1", "M1"],
            "ON_Time": [30, 70],
            "OFF_Time": [10, 20],
            "Avg_Cycle": [10, 10],
            "Weight": [100, 200],
            "Prs_Weight": [1000, 1000],
            "NAU_prs": [3, 14],
            "Discard_prs": [0, 0],
        }
    )
