from nautilus_mes_base import AppConfig
from nautilus_mes_base import MESOrchestra
from nautilus_mes_base.utils import parse_start_date
from app.services.utils import estimate_st_output_prs, validate_throughput
import pandas as pd
import numpy as np
import math


def handle_mach_view(start_time:str, end_time:str, shift:int)->pd.DataFrame:
    config = AppConfig.from_env()
    mes_nau = MESOrchestra.from_config(config)

    start_dt = parse_start_date(start_time)
    end_dt = parse_start_date(end_time)

    if end_dt < start_dt:
        raise SystemExit("End date must be on or after the start date.")
    
    df = mes_nau.generate_mes(start_dt, end_dt, shift)
    df["Shift_Start_Time"] = df["Shift_Start_Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["ST_prs"] = df[["Avg_Cycle", "ON_Time", "OFF_Time"]].apply(estimate_st_output_prs, axis=1)
    df["ON_Time_Occupation"] = (df["ON_Time"] / (df["ON_Time"] + df["OFF_Time"])).round(2)
    df["Real_prs"] = df[["NAU_prs", "ST_prs", "MES_prs", "ON_Time", "Discard_prs", "Avg_Cycle"]].apply(validate_throughput, axis=1)
    df["Mach_Efficiency"] = (df["Real_prs"]/df["ST_prs"]).round(2)
    df.loc[df["ON_Time"]==0, "Mach_Efficiency"] = np.nan
    df["Comment"] = ""
    df.loc[df["Mach_Efficiency"] >= 0.8, "Comment"] = "Good"
    df.loc[df["Mach_Efficiency"] < 0.8, "Comment"] = "Low Ef"
    df = df[["MachID", "Shift_Start_Time", 'Style_Code', "Weight", "MES_prs", "NAU_prs", "ON_Time", "OFF_Time", "ON_Time_Occupation", "Mach_Efficiency", "Comment"]]
    df = df.reset_index(names="id")
    df = df.astype(object).where(pd.notnull(df), None)
    return df




