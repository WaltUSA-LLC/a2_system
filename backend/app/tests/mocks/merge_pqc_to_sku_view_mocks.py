import pandas as pd


def make_base_sku_view_df() -> pd.DataFrame:
    """
    Mimic the aggregated SKU-info DataFrame built by handle_sku_view before
    PQC metrics are merged in.
    """
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["ABC", "XYZ", "QWE"],
            "Shift_Start_Time": [shift_time, shift_time, shift_time],
            "Mach_cnt": [2, 1, 1],
            "NAU_prs": [6, 5, 4],
            "MES_prs": [8, 7, 5],
            "Discard_prs": [3, 1, 0],
            "Discard_percent": [0.333, 0.167, 0.0],
            "ON_Time_Occupation": [0.8, 0.9, 1.0],
            "Efficiency": [0.4, 0.7, 0.5],
        }
    )


def make_multi_sku_shift_view_df() -> pd.DataFrame:
    shift_1 = pd.Timestamp("2026-05-01 07:00:00")
    shift_2 = pd.Timestamp("2026-05-01 19:00:00")

    return pd.DataFrame(
        {
            "Style_Code": ["ABC", "XYZ", "QWE"],
            "Shift_Start_Time": [shift_1, shift_2, shift_2],
            "Mach_cnt": [2, 2, 1],
            "NAU_prs": [6, 7, 3],
            "MES_prs": [8, 9, 4],
            "Discard_prs": [3, 2, 1],
            "Discard_percent": [0.333, 0.222, 0.25],
            "ON_Time_Occupation": [0.8, 0.75, 0.5],
            "Efficiency": [0.4, 0.6, 0.4],
        }
    )


def make_sku_view_df_with_unmatched_rows() -> pd.DataFrame:
    df = make_multi_sku_shift_view_df()
    unmatched_rows = pd.DataFrame(
        {
            "Style_Code": ["ABC", "MISSING"],
            "Shift_Start_Time": [
                pd.Timestamp("2026-05-01 19:00:00"),
                pd.Timestamp("2026-05-02 07:00:00"),
            ],
            "Mach_cnt": [1, 1],
            "NAU_prs": [4, 2],
            "MES_prs": [5, 3],
            "Discard_prs": [0, 0],
            "Discard_percent": [0.0, 0.0],
            "ON_Time_Occupation": [1.0, 1.0],
            "Efficiency": [0.5, 0.3],
        }
    )

    return pd.concat([df, unmatched_rows], ignore_index=True)
