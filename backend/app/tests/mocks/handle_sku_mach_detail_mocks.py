import numpy as np
import pandas as pd


def make_empty_sku_mach_detail_df() -> pd.DataFrame:
    return pd.DataFrame()


def make_base_sku_mach_detail_df() -> pd.DataFrame:
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Style_Code": [" abc red", "ABC blue ", "xyz black"],
            "Shift_Start_Time": [shift_time, shift_time, shift_time],
            "MachID": ["M2", "M1", "M3"],
            "ON_Time": [80, 60, 90],
            "OFF_Time": [20, 40, 10],
            "Avg_Cycle": [10, 10, 10],
            "Weight": [8, 5, 7],
            "Prs_Weight": [1000, 1000, 1000],
            "NAU_prs": [6, 4, 5],
            "Discard_prs": [1, 2, 3],
        }
    )


def make_sku_mach_detail_df_without_matching_style() -> pd.DataFrame:
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["xyz black", "qwe white"],
            "Shift_Start_Time": [shift_time, shift_time],
            "MachID": ["M1", "M2"],
            "ON_Time": [80, 70],
            "OFF_Time": [20, 30],
            "Avg_Cycle": [10, 10],
            "Weight": [7, 6],
            "Prs_Weight": [1000, 1000],
            "NAU_prs": [5, 4],
            "Discard_prs": [0, 0],
        }
    )


def make_sku_mach_detail_df_for_metrics_and_comments() -> pd.DataFrame:
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["abc red", "ABC blue", "abc green"],
            "Shift_Start_Time": [shift_time, shift_time, shift_time],
            "MachID": ["M1", "M2", "M3"],
            "ON_Time": [80, 50, 1],
            "OFF_Time": [20, 50, 2],
            "Avg_Cycle": [10, 10, 3],
            "Weight": [8, 7, 1],
            "Prs_Weight": [1000, 1000, 1000],
            "NAU_prs": [6, 5, 1],
            "Discard_prs": [1, 2, 3],
        }
    )


def make_unsorted_sku_mach_detail_df() -> pd.DataFrame:
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["abc red", "ABC blue", "ABC green"],
            "Shift_Start_Time": [shift_time, shift_time, shift_time],
            "MachID": ["M3", "M1", "M2"],
            "ON_Time": [70, 80, 60],
            "OFF_Time": [30, 20, 40],
            "Avg_Cycle": [10, 10, 10],
            "Weight": [7, 8, 6],
            "Prs_Weight": [1000, 1000, 1000],
            "NAU_prs": [5, 6, 4],
            "Discard_prs": [3, 1, 2],
        }
    )


def make_sku_mach_detail_df_with_invalid_style_code() -> pd.DataFrame:
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["", None, "abc red"],
            "Shift_Start_Time": [shift_time, shift_time, shift_time],
            "MachID": ["M1", "M2", "M3"],
            "ON_Time": [100, 100, 80],
            "OFF_Time": [0, 0, 20],
            "Avg_Cycle": [10, 10, 10],
            "Weight": [3, 5, 8],
            "Prs_Weight": [1000, 1000, 1000],
            "NAU_prs": [2, 4, 6],
            "Discard_prs": [0, 0, 0],
        }
    )


def make_sku_mach_detail_df_with_nan_discard_prs() -> pd.DataFrame:
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
            "NAU_prs": [4],
            "Discard_prs": [np.nan],
        }
    )


def make_sku_mach_detail_df_with_zero_discard_denominator() -> pd.DataFrame:
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
