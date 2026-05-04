from extractors import MESExtractor
from app.services.utils import extract_base_data, clean_weight, estimate_st_output_prs, estimate_mes_output_prs
import pandas as pd
import numpy as np

def handle_shift_view(start_time:str, end_time:str, shift:int)->pd.DataFrame:
    df = extract_base_data(MESExtractor, start_time, end_time, shift)
    df = clean_weight(df)
    df["MES_prs"] = df[["Weight", "Prs_Weight"]].apply(estimate_mes_output_prs, axis=1)
    df["Shift_Start_Time"] = df["Shift_Start_Time"].dt.strftime("%Y-%m-%d %H:%M:%S")

    df_on_mach = df[df["ON_Time"]>300]
    df_on_mach["ST_prs"] = df_on_mach[["Avg_Cycle", "ON_Time", "OFF_Time"]].apply(estimate_st_output_prs, axis=1)
    # total throughput 
    s_nau_prs = df_on_mach.groupby("Shift_Start_Time")["NAU_prs"].sum()
    s_mes_prs = df_on_mach.groupby("Shift_Start_Time")["MES_prs"].sum()
    s_st_prs = df_on_mach.groupby("Shift_Start_Time")["ST_prs"].sum()
    s_eff = (s_mes_prs / s_st_prs).round(3)

    # total running machine
    s_run_mach = df_on_mach.groupby("Shift_Start_Time")["MachID"].nunique()
    s_on_time = df_on_mach.groupby("Shift_Start_Time")["ON_Time"].sum()
    s_off_time = df_on_mach.groupby("Shift_Start_Time")["OFF_Time"].sum()
    s_time_ocup = (s_on_time/(s_on_time+s_off_time)).round(3)

    df_shift = pd.DataFrame({"Mach_cnt": s_run_mach,
                             "NAU_prs": s_nau_prs,
                             "MES_prs": s_mes_prs,
                             "ST_prs": s_st_prs,
                             "eff": s_eff,
                             "Time_Occupation": s_time_ocup
                            });

    df_shift.reset_index(inplace=True)
    df_shift = df_shift.reset_index(names="id")
    df_shift = df_shift.replace([np.nan, np.inf, -np.inf], None)

    return df_shift
