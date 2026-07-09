from extractors import MESExtractor
from app.services.pqc_view import merge_pqc_to_sku_view, merge_pqc_to_mach_dialog
from app.services.utils import estimate_st_output_prs, \
    estimate_mes_output_prs, \
    extract_base_data, \
    clean_weight, \
    filterShutdownMach, \
    distributeWeightForSameMach, \
    determine_mach_line, \
    enhance_mes_by_nau
import pandas as pd
import numpy as np


def handle_sku_view(start_time:str, end_time:str, shift:int)->pd.DataFrame:
    df = extract_base_data(MESExtractor, start_time, end_time, shift)
    if len(df)==0:
        return pd.DataFrame()
    df = distributeWeightForSameMach(df)
    df = clean_weight(df)
    df = filterShutdownMach(df)
    if len(df)==0:
        return pd.DataFrame()
    df["MES_prs"] = df[["Weight", "Prs_Weight"]].apply(estimate_mes_output_prs, axis=1)
    df["MES_prs"] = enhance_mes_by_nau(df)
    df["Style_Code"] = df["Style_Code"].apply(lambda x: x.strip().split()[0].upper() if isinstance(x, str) and x.strip() else None)
    
    #count mach
    df_mach_cnt = df.groupby(["Style_Code", "Shift_Start_Time"])["MachID"].nunique()
    #calc on time occupation
    df_on_time = df.groupby(["Style_Code", "Shift_Start_Time"])["ON_Time"].sum()
    df_off_time = df.groupby(["Style_Code", "Shift_Start_Time"])["OFF_Time"].sum()
    df_on_time_occupation = df_on_time/(df_on_time + df_off_time)
    #calc sku eff
    df["ST_prs"] = df[["Avg_Cycle", "ON_Time", "OFF_Time"]].apply(estimate_st_output_prs, axis=1)
    df_nau_prs = df.groupby(["Style_Code", "Shift_Start_Time"])["NAU_prs"].sum()
    df_mes_prs = df.groupby(["Style_Code", "Shift_Start_Time"])["MES_prs"].sum()
    df_discard_prs = df.groupby(["Style_Code", "Shift_Start_Time"])["Discard_prs"].sum()
    df_discard_percent = (df_discard_prs/(df_nau_prs+df_discard_prs)).round(3)
    df_st_prs = df.groupby(["Style_Code", "Shift_Start_Time"])["ST_prs"].agg(lambda s: np.nan if s.isna().any() else s.sum())
    df_sku_eff = df_mes_prs/df_st_prs

    df_sku=pd.DataFrame({"Mach_cnt": df_mach_cnt,
                "NAU_prs": df_nau_prs,
                "MES_prs": df_mes_prs,
                "Discard_prs": df_discard_prs,
                "Discard_percent": df_discard_percent,
                "ON_Time_Occupation": df_on_time_occupation,
                "Efficiency":df_sku_eff})
    df_sku.reset_index(inplace=True)
    df_sku = merge_pqc_to_sku_view(df_sku, start_time, end_time, shift)
    df_sku = df_sku.reset_index(names="id")
    df_sku = df_sku.replace([np.nan, np.inf, -np.inf], None)
    df_sku["Shift_Start_Time"] = df_sku["Shift_Start_Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    # filter out residual sku
    return df_sku


def handle_sku_mach_detail(start_time:str, end_time:str, shift:int, style:str)->pd.DataFrame:
    df = extract_base_data(MESExtractor, start_time, end_time, shift)
    if len(df)==0:
        return pd.DataFrame()
    df = distributeWeightForSameMach(df)
    df = clean_weight(df)
    df = filterShutdownMach(df)
    if len(df)==0:
        return pd.DataFrame()
    df["MES_prs"] = df[["Weight", "Prs_Weight"]].apply(estimate_mes_output_prs, axis=1)
    df["Style_Code_wo_size"] = df["Style_Code"].apply(lambda x: x.strip().split()[0].upper() if isinstance(x, str) and x.strip() else None)
    df["Style_Code"] = df["Style_Code"].apply(lambda x: x.strip().upper() if isinstance(x, str) and x.strip() else None)

    #filter style
    df = df[df["Style_Code_wo_size"]==style]

    #all mach info
    df["Shift_Start_Time"] = df["Shift_Start_Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["ST_prs"] = df[["Avg_Cycle", "ON_Time", "OFF_Time"]].apply(estimate_st_output_prs, axis=1)
    df["ON_Time_Occupation"] = (df["ON_Time"] / (df["ON_Time"] + df["OFF_Time"])).round(3)
    df["Mach_Efficiency"] = (df["MES_prs"]/df["ST_prs"]).round(3)
    df["Discard_percent"] = (df["Discard_prs"] / (df["NAU_prs"]+df["Discard_prs"])).round(3)
    #df.loc[df["ON_Time"]==0, "Mach_Efficiency"] = np.nan
    df["Comment"] = ""
    df.loc[df["Mach_Efficiency"] >= 0.8, "Comment"] = "Good"
    df.loc[df["Mach_Efficiency"] < 0.8, "Comment"] = "Low Ef"
    df["LineID"] = df["MachID"].apply(determine_mach_line)

    df = df[["LineID", "MachID", "Shift_Start_Time", 'Style_Code', "MES_prs", "NAU_prs", "Discard_prs", "Discard_percent", "ON_Time", "OFF_Time", "ON_Time_Occupation", "Mach_Efficiency", "Comment"]]
    df = merge_pqc_to_mach_dialog(df, start_time, shift)
    df = df.reset_index(names="id")
    df = df.replace([np.nan, np.inf, -np.inf], None)
    df = df.sort_values(by=["LineID", "MachID"], ascending=[True, True])
    return df
