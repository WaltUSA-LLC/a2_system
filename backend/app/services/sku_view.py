from extractors import MESExtractor
from app.services.utils import estimate_st_output_prs, \
    estimate_mes_output_prs, \
    validate_throughput, \
    extract_base_data, \
    clean_weight, \
    filterShutdownMach, \
    distributeWeightForSameMach
import pandas as pd
import numpy as np


def handle_sku_view(start_time:str, end_time:str, shift:int)->pd.DataFrame:
    df = extract_base_data(MESExtractor, start_time, end_time, shift)
    df = clean_weight(df)
    df = filterShutdownMach(df)
    df = distributeWeightForSameMach(df)
    df["MES_prs"] = df[["Weight", "Prs_Weight"]].apply(estimate_mes_output_prs, axis=1)
    df["Style_Code"] = df["Style_Code"].apply(lambda x: x.strip().split()[0] if isinstance(x, str) and x.strip() else None)
    
    #count mach
    df_mach_cnt = df.groupby(["Style_Code", "Shift_Start_Time"])["MachID"].nunique()
    #calc on time occupation
    df_on_time = df.groupby(["Style_Code", "Shift_Start_Time"])["ON_Time"].sum()
    df_off_time = df.groupby(["Style_Code", "Shift_Start_Time"])["OFF_Time"].sum()
    df_on_time_occupation = df_on_time/(df_on_time + df_off_time)
    #calc sku eff
    df["ST_prs"] = df[["Avg_Cycle", "ON_Time", "OFF_Time"]].apply(estimate_st_output_prs, axis=1)
    df["Real_prs"] = df[["NAU_prs", "ST_prs", "MES_prs", "ON_Time", "Discard_prs", "Avg_Cycle"]].apply(validate_throughput, axis=1)
    df_nau_prs = df.groupby(["Style_Code", "Shift_Start_Time"])["NAU_prs"].sum()
    df_mes_prs = df.groupby(["Style_Code", "Shift_Start_Time"])["MES_prs"].sum()
    #df_real_prs = df.groupby(["Style_Code", "Shift_Start_Time"])["Real_prs"].sum()
    df_st_prs = df.groupby(["Style_Code", "Shift_Start_Time"])["ST_prs"].sum()
    df_sku_eff = df_mes_prs/df_st_prs

    df_sku=pd.DataFrame({"Mach_cnt": df_mach_cnt,
                "NAU_prs": df_nau_prs,
                "MES_prs": df_mes_prs,
                "ON_Time_Occupation": df_on_time_occupation,
                "Efficiency":df_sku_eff})
    df_sku.reset_index(inplace=True)
    df_sku = df_sku.reset_index(names="id")
    df_sku = df_sku.replace([np.nan, np.inf, -np.inf], None)
    df_sku["Shift_Start_Time"] = df_sku["Shift_Start_Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    # filter out residual sku
    return df_sku


def handle_sku_mach_detail(start_time:str, end_time:str, shift:int, style:str)->pd.DataFrame:
    df = extract_base_data(MESExtractor, start_time, end_time, shift)
    df = clean_weight(df)
    df = filterShutdownMach(df)
    df = distributeWeightForSameMach(df)
    df["MES_prs"] = df[["Weight", "Prs_Weight"]].apply(estimate_mes_output_prs, axis=1)
    df["Style_Code_wo_size"] = df["Style_Code"].apply(lambda x: x.strip().split()[0] if isinstance(x, str) and x.strip() else None)

    #filter style
    df = df[df["Style_Code_wo_size"]==style]

    #all mach info
    df["Shift_Start_Time"] = df["Shift_Start_Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["ST_prs"] = df[["Avg_Cycle", "ON_Time", "OFF_Time"]].apply(estimate_st_output_prs, axis=1)
    df["ON_Time_Occupation"] = (df["ON_Time"] / (df["ON_Time"] + df["OFF_Time"])).round(2)
    #df["Real_prs"] = df[["NAU_prs", "ST_prs", "MES_prs", "ON_Time", "Discard_prs", "Avg_Cycle"]].apply(validate_throughput, axis=1)
    df["Mach_Efficiency"] = (df["MES_prs"]/df["ST_prs"]).round(2)
    df.loc[df["ON_Time"]==0, "Mach_Efficiency"] = np.nan
    df["Comment"] = ""
    df.loc[df["Mach_Efficiency"] >= 0.8, "Comment"] = "Good"
    df.loc[df["Mach_Efficiency"] < 0.8, "Comment"] = "Low Ef"
    df = df[["MachID", "Shift_Start_Time", 'Style_Code', "MES_prs", "NAU_prs", "ON_Time", "OFF_Time", "ON_Time_Occupation", "Mach_Efficiency", "Comment"]]
    df = df.reset_index(names="id")
    df = df.astype(object).where(pd.notnull(df), None)
    df = df.sort_values(by="MachID", ascending=True)
    return df