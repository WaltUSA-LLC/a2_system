import math
import pandas as pd
import numpy as np

from extractors import AppConfig
from extractors import BaseExtractor, StaffScheduleExtractor
from extractors.utils import parse_start_date

# def validate_throughput(rec:pd.Series) -> pd.Series:
#     nau = rec["NAU_prs"]
#     weight = rec["MES_prs"]
#     on_time = rec["ON_Time"]
#     avg_cycle = rec["Avg_Cycle"]
#     discard = rec["Discard_prs"]
#     theory_expect = math.ceil(on_time/avg_cycle/2) if not pd.isna(avg_cycle) else np.nan
#     act_expect = theory_expect - discard if not pd.isna(theory_expect) else np.nan
#     buffer = 10
    
#     if (nau==0 and on_time==0) or (weight==0 and on_time==0):
#         return 0
#     if (weight<0 or weight>theory_expect+buffer or pd.isna(weight)) and (nau<0 or nau>theory_expect+buffer or pd.isna(nau)):
#         return np.nan
#     elif (weight<0 or weight>theory_expect+buffer or pd.isna(weight)):
#         return nau
#     else:
#         return weight


def estimate_mes_output_prs(rec: pd.Series) -> int:
    if pd.isna(rec["Prs_Weight"]) or rec["Prs_Weight"] == 0:
        return np.nan
    if pd.isna(rec["Weight"]):
        return np.nan
    return math.floor(rec["Weight"]/(rec["Prs_Weight"]/1000))   

   
def estimate_st_output_prs(rec: pd.Series) -> int:
    if pd.isna(rec["Avg_Cycle"]) or rec["Avg_Cycle"] == 0:
        return np.nan
    if pd.isna(rec["ON_Time"]+rec["OFF_Time"]):
        return np.nan
    return math.floor((rec["ON_Time"]+rec["OFF_Time"])/rec["Avg_Cycle"]/2)


def clean_weight(df: pd.DataFrame) -> pd.DataFrame:
    cleaned_df = df.copy()
    if "Weight" in cleaned_df.columns:
        mask = (cleaned_df["Weight"] > 0) & (cleaned_df["Weight"] < 1)
        cleaned_df.loc[mask, "Weight"] = 0
    return cleaned_df


def filterShutdownMach(df: pd.DataFrame) -> pd.DataFrame:
    cleaned_df = df.copy()
    cleaned_df = cleaned_df[(cleaned_df["Weight"]>0)|(cleaned_df["NAU_prs"]>0)|(cleaned_df["ON_Time"]>600)]
    return cleaned_df


def distributeWeightForSameMach(df: pd.DataFrame) -> pd.DataFrame:
    cleaned_df = df.copy()
    s_on_time_sum = cleaned_df.groupby(["MachID", "Shift_Start_Time"])["ON_Time"].transform("sum")
    s_group_size = cleaned_df.groupby(["MachID", "Shift_Start_Time"])["ON_Time"].transform("size")

    cleaned_df["Weight"] = np.where(
        s_on_time_sum > 0,
        cleaned_df["Weight"] * (cleaned_df["ON_Time"] / s_on_time_sum),
        cleaned_df["Weight"] / s_group_size
    )
    #print(cleaned_df[cleaned_df["MachID"]==100])
    return cleaned_df


def get_staff_schedule_table(start_time: str, end_time: str):
    df = extract_base_data(StaffScheduleExtractor, start_time, end_time)
    # make sure ShiftStartTime is datetime
    df["ShiftStartTime"] = pd.to_datetime(df["ShiftStartTime"])

    pivot_df = df.pivot_table(
            index="ShiftStartTime",
            columns="RoleName",
            values="FirstName",
            aggfunc=lambda x: ", ".join(x.dropna().astype(str))
    ).reset_index()

    return pivot_df


def extract_base_data(extractor_cls: type[BaseExtractor], start_time:str, end_time:str, shift:int=0)->pd.DataFrame:
    config = AppConfig.from_env()
    ext = extractor_cls.from_config(config)

    start_dt = parse_start_date(start_time)
    end_dt = parse_start_date(end_time)

    if end_dt < start_dt:
        raise SystemExit("End date must be on or after the start date.")
    
    return ext.extract(start_dt, end_dt, shift)