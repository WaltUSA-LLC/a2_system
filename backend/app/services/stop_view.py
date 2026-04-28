from extractors import AppConfig
from extractors import StopExtractor
from extractors.utils import parse_start_date
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


def handle_stop_view_by_code(start_time:str, end_time:str, shift:int)->pd.DataFrame:
    config = AppConfig.from_env()
    nau_stop = StopExtractor.from_config(config)

    start_dt = parse_start_date(start_time)
    end_dt = parse_start_date(end_time)

    if end_dt < start_dt:
        raise SystemExit("End date must be on or after the start date.")
    
    df = nau_stop.extract(start_dt, end_dt)
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
                                    "dur_sum": df_dur_sum,
                                    "dur_med": df_dur_med  })
    df_stop_by_code = df_stop_by_code.sort_values(["freq", "Mach_cnt", "dur_sum"], ascending=[False, False, False])
    df_stop_by_code.reset_index(inplace=True)
    df_stop_by_code = df_stop_by_code.reset_index(names="id")

    #chart
    df_freq_sort = df_stop_by_code[["Stop_code", "freq"]].sort_values("freq", ascending=False)
    df_mach_sort = df_stop_by_code[["Stop_code", "Mach_cnt"]].sort_values("Mach_cnt", ascending=False)
    df_dur_sum_sort = df_stop_by_code[["Stop_code", "dur_sum"]].sort_values("dur_sum", ascending=False)
    df_dur_med_sort = df_stop_by_code[["Stop_code", "dur_med"]].sort_values("dur_med", ascending=False)
    return df_stop_by_code, \
           df_freq_sort.iloc[:min(10,len(df))], \
           df_mach_sort.iloc[:min(10,len(df))], \
           df_dur_sum_sort.iloc[:min(10,len(df))],\
           df_dur_med_sort.iloc[:min(10,len(df))]


def handle_stop_view_by_mach(start_time:str, end_time:str, shift:int)->pd.DataFrame:
    config = AppConfig.from_env()
    nau_stop = StopExtractor.from_config(config)

    start_dt = parse_start_date(start_time)
    end_dt = parse_start_date(end_time)

    if end_dt < start_dt:
        raise SystemExit("End date must be on or after the start date.")
    
    df = nau_stop.extract(start_dt, end_dt)
    df["Start_Shift_Time"] = df["Stop_time"].apply(determin_start_shift_time)
    if shift==1:
        df = df[df["Start_Shift_Time"].str.contains("07:00:00", na=False)]
    elif shift==2:
        df = df[df["Start_Shift_Time"].str.contains("19:00:00", na=False)]
    else:
        pass
    
    #table
    df["Style_Code"] = df["Style_Code"].apply(lambda x: x.strip().split()[0] if isinstance(x, str) and x.strip() else None)
    df["Description"] = df["Description"].str.strip()
    df_freq = df.groupby(["MachID", "Style_Code"]).size()
    df_stop_by_mach = pd.DataFrame({"freq":df_freq,})
    df_stop_by_mach = df_stop_by_mach.sort_values(["MachID", "Style_Code", "freq"], ascending=[True, True, False])
    df_stop_by_mach.reset_index(inplace=True)
    df_stop_by_mach = df_stop_by_mach.reset_index(names="id")

    #chart
    df_freq = df.groupby(["MachID"]).size()
    df_stop_chart_mach = pd.DataFrame({"freq":df_freq,})
    df_stop_chart_mach = df_stop_chart_mach.sort_values(["freq"], ascending=[False])
    df_stop_chart_mach.reset_index(inplace=True)

    return df_stop_by_mach, df_stop_chart_mach.iloc[:min(10, len(df_stop_chart_mach))]


def handle_stop_mach_detail(start_time:str, end_time:str, shift:int, mach:int, style:str)->pd.DataFrame:
    config = AppConfig.from_env()
    nau_stop = StopExtractor.from_config(config)

    start_dt = parse_start_date(start_time)
    end_dt = parse_start_date(end_time)

    if end_dt < start_dt:
        raise SystemExit("End date must be on or after the start date.")
    
    df = nau_stop.extract(start_dt, end_dt)
    df["Start_Shift_Time"] = df["Stop_time"].apply(determin_start_shift_time)
    df["Style_Code"] = df["Style_Code"].apply(lambda x: x.strip().split()[0] if isinstance(x, str) and x.strip() else None)
    if shift==1:
        df = df[(df["Start_Shift_Time"].str.contains("07:00:00", na=False))&
                (df["MachID"]==mach)&
                (df["Style_Code"]==style)]
    elif shift==2:
        df = df[(df["Start_Shift_Time"].str.contains("19:00:00", na=False))&
                (df["MachID"]==mach)&
                (df["Style_Code"]==style)]
    else:
        df = df[(df["MachID"]==mach)&
                (df["Style_Code"]==style)]
    #print(len(df))
    df["Recover_time"] = df["Recover_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["Stop_time"] = df["Stop_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["Description"] = df["Description"].str.strip()
    df = df.sort_values(["Start_Shift_Time", "dur_minute"], ascending=[True, False])
    df = df.reset_index(names="id")
    df = df.astype(object).where(pd.notnull(df), None)
    return df


def handle_stop_code_detail(start_time:str, end_time:str, shift:int, stop_code:int)->pd.DataFrame:
    config = AppConfig.from_env()
    nau_stop = StopExtractor.from_config(config)

    start_dt = parse_start_date(start_time)
    end_dt = parse_start_date(end_time)

    if end_dt < start_dt:
        raise SystemExit("End date must be on or after the start date.")
    
    df = nau_stop.extract(start_dt, end_dt)
    df["Start_Shift_Time"] = df["Stop_time"].apply(determin_start_shift_time)
    df["Style_Code"] = df["Style_Code"].apply(lambda x: x.strip().split()[0] if isinstance(x, str) and x.strip() else None)
    if shift==1:
        df = df[(df["Start_Shift_Time"].str.contains("07:00:00", na=False))&
                (df["Stop_code"]==stop_code)]
    elif shift==2:
        df = df[(df["Start_Shift_Time"].str.contains("19:00:00", na=False))&
                (df["Stop_code"]==stop_code)]
    else:
        df = df[(df["Stop_code"]==stop_code)]

    df_dur_sum = df.groupby(["MachID", "Style_Code"])["dur_minute"].sum()
    df_dur_med = df.groupby(["MachID", "Style_Code"])["dur_minute"].median()
    df_freq = df.groupby(["MachID", "Style_Code"]).size()

    df = pd.DataFrame({"freq":df_freq,
                        "dur_sum": df_dur_sum,
                        "dur_med": df_dur_med  })
    df = df.sort_values(["MachID", "freq"], ascending=[True, False])
    df.reset_index(inplace=True)
    df = df.reset_index(names="id")
    return df
    



