import pandas as pd

"""
provide mach info for the merge test
"""

def make_base_mach_dialog_df() -> pd.DataFrame:
    """
    Mimic the machine-info DataFrame built by machine detail handlers before
    PQC metrics are merged in.
    """
    shift_time = "2026-05-01 07:00:00"

    return pd.DataFrame(
        {
            "MachID": ["M1", "M2", "M3", "M4"],
            "Shift_Start_Time": [shift_time, shift_time, shift_time, shift_time],
            "Style_Code": ["ABC RED", "ABC BLUE", "XYZ BLACK", "QWE WHITE"],
            "MES_prs": [8, 5, 7, 4],
            "NAU_prs": [6, 4, 5, 3],
            "Comment": ["Good", "Low Ef", "Good", "Low Ef"],
        }
    )


def make_same_machine_different_style_dialog_df() -> pd.DataFrame:
    shift_time = "2026-05-01 07:00:00"

    return pd.DataFrame(
        {
            "MachID": ["M1", "M1", "M2"],
            "Shift_Start_Time": [shift_time, shift_time, shift_time],
            "Style_Code": ["ABC RED", "ABC BLUE", "ABC BLUE"],
            "MES_prs": [8, 6, 5],
            "NAU_prs": [6, 5, 4],
        }
    )
