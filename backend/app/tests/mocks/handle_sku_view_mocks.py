import pandas as pd
import numpy as np

def make_empty_sku_df() -> pd.DataFrame:
    return pd.DataFrame()


def make_base_sku_df() -> pd.DataFrame:
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Style_Code": [" abc red", "ABC blue ", "abc"],
            "Shift_Start_Time": [shift_time, shift_time, shift_time],
            "MachID": ["M1", "M2", "M1"],
            "ON_Time": [100, 60, 10],
            "OFF_Time": [0, 20, 10],
            "Avg_Cycle": [10, 10, 10],
            "Weight": [3, 5, 3],
            "Prs_Weight": [1000, 1000, 1000],
            "NAU_prs": [2, 4, 2],
            "Discard_prs": [0, 0, 0],
        }
    )


def make_multi_sku_multi_shift_df() -> pd.DataFrame:
    shift_1 = pd.Timestamp("2026-05-01 07:00:00")
    shift_2 = pd.Timestamp("2026-05-01 19:00:00")

    return pd.DataFrame(
        {
            "Style_Code": [" abc red", "ABC blue", "xyz black", "ABC green",],
            "Shift_Start_Time": [shift_1, shift_1, shift_1, shift_2,],
            "MachID": ["M1", "M2", "M3", "M4",],
            "ON_Time": [100, 60, 80, 90,],
            "OFF_Time": [0, 20, 20, 10,],
            "Avg_Cycle": [10, 10, 10, 10,],
            "Weight": [3, 5, 4, 6,],
            "Prs_Weight": [1000, 1000, 1000, 1000,],
            "NAU_prs": [2, 4, 7, 3,],
            "Discard_prs": [0, 0, 0, 0,],
        }
    )


def make_sku_df_with_nan_st_prs() -> pd.DataFrame:
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["xyz black", "XYZ white"],
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



def make_sku_df_with_zero_st_prs() -> pd.DataFrame:
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["aaa test"],
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


def make_sku_df_with_invalid_style_code() -> pd.DataFrame:
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["", None],
            "Shift_Start_Time": [shift_time, shift_time],
            "MachID": ["M1", "M2"],
            "ON_Time": [100, 100],
            "OFF_Time": [0, 0],
            "Avg_Cycle": [10, 10],
            "Weight": [3, 5],
            "Prs_Weight": [1000, 1000],
            "NAU_prs": [2, 4],
            "Discard_prs": [0, 0],
        }
    )