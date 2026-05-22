import numpy as np
import pandas as pd
from app.services.utils import get_staff_schedule_table
from cores.constants import DAY_SHIFT, NIGHT_SHIFT, DAY_SHIFT_START, NIGHT_SHIFT_START

def fetch_staff_info_by_date_and_shift(date:str, shift:str)->pd.DataFrame:
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


def merge_staff_info_to_view(df:pd.DataFrame, start_time:str, end_time:str)->pd.DataFrame:
    df_staff = get_staff_schedule_table(start_time, end_time)
    df["Shift_Start_Time"] = pd.to_datetime(df["Shift_Start_Time"]) #make sure Shift_Start_Time is datetime
    df = df.merge(df_staff, left_on="Shift_Start_Time", right_on="ShiftStartTime", how="left")
    df = df.drop(columns=["ShiftStartTime"], errors="ignore")
    df["Shift_Start_Time"] = df["Shift_Start_Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df = df.replace([np.nan, np.inf, -np.inf], None)
    return df
