import pandas as pd
import numpy as np


def make_empty_shift_df() -> pd.DataFrame:
    return pd.DataFrame()


def make_base_shift_df() -> pd.DataFrame:
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["abc red", "ABC blue", "abc green"],
            "Shift_Start_Time": [shift_time, shift_time, shift_time],
            "MachID": ["M1", "M2", "M1"],
            "ON_Time": [100, 60, 10],
            "OFF_Time": [0, 20, 10],
            "Avg_Cycle": [10, 10, 10],
            "Weight": [3, 5, 3],
            "Prs_Weight": [1000, 1000, 1000],
            "NAU_prs": [2, 4, 2],
            "Discard_prs": [1, 2, 3],
        }
    )


def make_multi_shift_df() -> pd.DataFrame:
    shift_1 = pd.Timestamp("2026-05-01 07:00:00")
    shift_2 = pd.Timestamp("2026-05-01 19:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["abc red", "ABC blue", "xyz black", "qwe white"],
            "Shift_Start_Time": [shift_1, shift_1, shift_2, shift_2],
            "MachID": ["M1", "M2", "M3", "M4"],
            "ON_Time": [100, 60, 90, 30],
            "OFF_Time": [0, 20, 10, 30],
            "Avg_Cycle": [10, 10, 10, 20],
            "Weight": [3, 5, 6, 4],
            "Prs_Weight": [1000, 1000, 1000, 1000],
            "NAU_prs": [2, 4, 3, 7],
            "Discard_prs": [1, 2, 3, 4],
        }
    )


def make_shift_df_with_duplicate_mach() -> pd.DataFrame:
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["abc red", "ABC blue", "abc green"],
            "Shift_Start_Time": [shift_time, shift_time, shift_time],
            "MachID": ["M1", "M2", "M1"],
            "ON_Time": [70, 60, 50],
            "OFF_Time": [30, 40, 50],
            "Avg_Cycle": [10, 10, 10],
            "Weight": [7, 6, 5],
            "Prs_Weight": [1000, 1000, 1000],
            "NAU_prs": [5, 4, 3],
            "Discard_prs": [1, 2, 3],
        }
    )


def make_shift_df_for_filter_shutdown() -> pd.DataFrame:
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["abc red", "ABC blue", "xyz black"],
            "Shift_Start_Time": [shift_time, shift_time, shift_time],
            "MachID": ["M_KEEP_1", "M_STOP", "M_KEEP_2"],
            "ON_Time": [100, 50, 60],
            "OFF_Time": [0, 50, 40],
            "Avg_Cycle": [10, 10, 20],
            "Weight": [8, 9, 4],
            "Prs_Weight": [1000, 1000, 1000],
            "NAU_prs": [6, 7, 3],
            "Discard_prs": [1, 99, 3],
            "Should_Filter": [False, True, False],
        }
    )


def make_shift_df_that_filters_to_empty() -> pd.DataFrame:
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["abc red", "ABC blue"],
            "Shift_Start_Time": [shift_time, shift_time],
            "MachID": ["M_STOP_1", "M_STOP_2"],
            "ON_Time": [100, 80],
            "OFF_Time": [0, 20],
            "Avg_Cycle": [10, 10],
            "Weight": [8, 6],
            "Prs_Weight": [1000, 1000],
            "NAU_prs": [6, 4],
            "Discard_prs": [0, 0],
            "Should_Filter": [True, True],
        }
    )


def make_shift_df_with_zero_st_prs() -> pd.DataFrame:
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["abc red"],
            "Shift_Start_Time": [shift_time],
            "MachID": ["M1"],
            "ON_Time": [1],
            "OFF_Time": [1],
            "Avg_Cycle": [0],
            "Weight": [10],
            "Prs_Weight": [1000],
            "NAU_prs": [1],
            "Discard_prs": [0],
        }
    )


def make_shift_df_with_zero_time() -> pd.DataFrame:
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["abc red"],
            "Shift_Start_Time": [shift_time],
            "MachID": ["M1"],
            "ON_Time": [0],
            "OFF_Time": [0],
            "Avg_Cycle": [10],
            "Weight": [5],
            "Prs_Weight": [1000],
            "NAU_prs": [1],
            "Discard_prs": [0],
        }
    )


def make_shift_df_with_nan_st_prs() -> pd.DataFrame:
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["abc red", "ABC blue"],
            "Shift_Start_Time": [shift_time, shift_time],
            "MachID": ["M1", "M2"],
            "ON_Time": [100, 60],
            "OFF_Time": [0, 20],
            "Avg_Cycle": [10, np.nan],
            "Weight": [3, 5],
            "Prs_Weight": [1000, 1000],
            "NAU_prs": [2, 4],
            "Discard_prs": [0, 0],
        }
    )


def make_shift_df_with_nan_discard_prs() -> pd.DataFrame:
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["abc red", "ABC blue"],
            "Shift_Start_Time": [shift_time, shift_time],
            "MachID": ["M1", "M2"],
            "ON_Time": [100, 60],
            "OFF_Time": [0, 20],
            "Avg_Cycle": [10, 10],
            "Weight": [3, 5],
            "Prs_Weight": [1000, 1000],
            "NAU_prs": [2, 4],
            "Discard_prs": [1, np.nan],
        }
    )


def make_shift_df_with_zero_discard_denominator() -> pd.DataFrame:
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["abc red"],
            "Shift_Start_Time": [shift_time],
            "MachID": ["M1"],
            "ON_Time": [100],
            "OFF_Time": [0],
            "Avg_Cycle": [10],
            "Weight": [5],
            "Prs_Weight": [1000],
            "NAU_prs": [0],
            "Discard_prs": [0],
        }
    )
