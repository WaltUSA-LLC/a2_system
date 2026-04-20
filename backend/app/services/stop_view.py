from nautilus_mes_base import AppConfig
from nautilus_mes_base import NAUStopOrchestra
from nautilus_mes_base.utils import parse_start_date
import pandas as pd
from datetime import time, timedelta

def determin_start_shift_time(stop_time:pd.Timestamp)->str:
    date = stop_time.strftime("%Y-%m-%d %H:%M:%S").split()[0]
    pre_date = (stop_time-timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S").split()[0]
    if time(0,0,0) <= stop_time.time() <= time(7,0,0):
        return pre_date+" 19:00:00"
    elif time(7,0,0) < stop_time.time() <= time(19,0,0):
        return date+" 07:00:00"
    else:
        return date+" 19:00:00"
    


def handle_stop_view_by_time(start_time:str, end_time:str, shift:int)->pd.DataFrame:
    config = AppConfig.from_env()
    nau_stop = NAUStopOrchestra.from_config(config)

    start_dt = parse_start_date(start_time)
    end_dt = parse_start_date(end_time)

    if end_dt < start_dt:
        raise SystemExit("End date must be on or after the start date.")
    
    df = nau_stop.generate_nau_stop(start_dt, end_dt)
    df["Start_Shift_Time"] = df["Stop_time"].apply(determin_start_shift_time)
    if shift==1:
        df = df[df["Start_Shift_Time"].str.contains("07:00:00", na=False)]
    elif shift==2:
        df = df[df["Start_Shift_Time"].str.contains("19:00:00", na=False)]
    else:
        pass
    df["Recover_time"] = df["Recover_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["Stop_time"] = df["Stop_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["Description"] = df["Description"].str.strip()
    df = df.sort_values(["Start_Shift_Time", "dur_minute"], ascending=[True, False])
    df = df.reset_index(names="id")
    df = df.astype(object).where(pd.notnull(df), None)
    return df


def handle_stop_view_by_code(start_time:str, end_time:str, shift:int)->pd.DataFrame:
    config = AppConfig.from_env()
    nau_stop = NAUStopOrchestra.from_config(config)

    start_dt = parse_start_date(start_time)
    end_dt = parse_start_date(end_time)

    if end_dt < start_dt:
        raise SystemExit("End date must be on or after the start date.")
    
    df = nau_stop.generate_nau_stop(start_dt, end_dt)
    df["Start_Shift_Time"] = df["Stop_time"].apply(determin_start_shift_time)
    if shift==1:
        df = df[df["Start_Shift_Time"].str.contains("07:00:00", na=False)]
    elif shift==2:
        df = df[df["Start_Shift_Time"].str.contains("19:00:00", na=False)]
    else:
        pass

    df["Description"] = df["Description"].str.strip()
    #count machs
    df_mach_cnt = df.groupby(["Stop_code", "Description"])["MachID"].nunique()
    df_freq = df.groupby(["Stop_code", "Description"]).size()
    #stop hours
    df_dur_sum = df.groupby(["Stop_code", "Description"])["dur_minute"].sum()
    df_dur_med = df.groupby(["Stop_code", "Description"])["dur_minute"].median()

    df_stop_by_code = pd.DataFrame({"Mach_cnt": df_mach_cnt,
                                    "freq":df_freq,
                                    "dur_minute_sum": df_dur_sum,
                                    "dur_minute_med": df_dur_med  })
    df_stop_by_code = df_stop_by_code.sort_values(["Mach_cnt", "dur_minute_sum"], ascending=[False, False])
    df_stop_by_code.reset_index(inplace=True)
    df_stop_by_code = df_stop_by_code.reset_index(names="id")
    return df_stop_by_code



