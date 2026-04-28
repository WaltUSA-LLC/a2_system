from extractors import MESExtractor
from app.services.utils import estimate_st_output_prs, validate_throughput, extract_base_data
import pandas as pd
import numpy as np
import math


def handle_mach_view(start_time:str, end_time:str, shift:int)->pd.DataFrame:
    df = extract_base_data(MESExtractor, start_time, end_time, shift)
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




