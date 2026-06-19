import pandas as pd


def make_base_shift_view_df() -> pd.DataFrame:
    """
    Mimic the aggregated shift-info DataFrame built by handle_shift_view before
    PQC metrics are merged in.
    """
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    return pd.DataFrame(
        {
            "id": [0],
            "Shift_Start_Time": [shift_time],
            "Mach_cnt": [2],
            "NAU_prs": [6],
            "MES_prs": [8],
            "Discard_prs": [3],
            "Discard_percent": [0.333],
            "ST_prs": [20],
            "eff": [0.4],
            "Time_Occupation": [0.8],
        }
    )


def make_multi_shift_view_df() -> pd.DataFrame:
    shift_1 = pd.Timestamp("2026-05-01 07:00:00")
    shift_2 = pd.Timestamp("2026-05-01 19:00:00")

    return pd.DataFrame(
        {
            "id": [0, 1],
            "Shift_Start_Time": [shift_1, shift_2],
            "Mach_cnt": [2, 3],
            "NAU_prs": [6, 10],
            "MES_prs": [8, 12],
            "Discard_prs": [3, 7],
            "Discard_percent": [0.333, 0.412],
            "ST_prs": [20, 30],
            "eff": [0.4, 0.4],
            "Time_Occupation": [0.8, 0.75],
        }
    )


def make_shift_view_df_with_unmatched_shift() -> pd.DataFrame:
    df = make_multi_shift_view_df()
    unmatched_row = pd.DataFrame(
        {
            "id": [2],
            "Shift_Start_Time": [pd.Timestamp("2026-05-02 07:00:00")],
            "Mach_cnt": [1],
            "NAU_prs": [4],
            "MES_prs": [5],
            "Discard_prs": [0],
            "Discard_percent": [0.0],
            "ST_prs": [10],
            "eff": [0.5],
            "Time_Occupation": [1.0],
        }
    )

    return pd.concat([df, unmatched_row], ignore_index=True)
