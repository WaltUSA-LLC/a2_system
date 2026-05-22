import numpy as np
from app.services.utils import get_staff_schedule_table
from cores.constants import DAY_SHIFT, NIGHT_SHIFT, DAY_SHIFT_START, NIGHT_SHIFT_START

def fetch_staff_info_by_date_and_shift(date:str, shift:str):
    df_staff = get_staff_schedule_table(date, date)
    if shift == DAY_SHIFT:
        df_staff = df_staff[df_staff["ShiftStartTime"].dt.time == DAY_SHIFT_START]
    elif shift == NIGHT_SHIFT:
        df_staff = df_staff[df_staff["ShiftStartTime"].dt.time == NIGHT_SHIFT_START]
    else:
        raise ValueError(f"Shift {shift} is invalid in handle_shift_mach_detail")
    df_staff = df_staff.drop(columns=["ShiftStartTime"], errors="ignore")
    df_staff = df_staff.replace([np.nan], None)
    return df_staff