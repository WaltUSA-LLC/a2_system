import logging
import math
import pandas as pd
import numpy as np

from extractors import AppConfig
from extractors import BaseExtractor
from extractors.utils import parse_start_date
from cores.constants import ON_MACH_THRESHOLD,\
    NAU_PRS_THRESHOLD,\
    NUM_MACH_IN_ZONE, \
    MES_WEIGH_THRESHOLD

logger = logging.getLogger(__name__)

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
    #this function is optional now (could be removed)
    cleaned_df = df.copy()
    if "Weight" in cleaned_df.columns:
        mask = (cleaned_df["Weight"] > 0) & (cleaned_df["Weight"] < 0.01) # set to 0.01 just want not enhance by nau frequently
        cleaned_df.loc[mask, "Weight"] = 0
    return cleaned_df


def filterShutdownMach(df: pd.DataFrame) -> pd.DataFrame:
    cleaned_df = df.copy()
    cleaned_df = cleaned_df[(cleaned_df["Weight"]>MES_WEIGH_THRESHOLD)|(cleaned_df["NAU_prs"]>NAU_PRS_THRESHOLD)|(cleaned_df["ON_Time"]>ON_MACH_THRESHOLD)]
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

def determine_mach_line(machID: int) -> int | None:
    if machID <= 0:
        return None
    if not isinstance(machID, int):
        return None

    if machID<=NUM_MACH_IN_ZONE and machID%2==1:
        return 1
    elif machID<=NUM_MACH_IN_ZONE and machID%2==0:
        return 2
    elif machID<=NUM_MACH_IN_ZONE*2 and machID%2==1:
        return 3
    elif machID<=NUM_MACH_IN_ZONE*2 and machID%2==0:
        return 4
    elif machID<=NUM_MACH_IN_ZONE*3 and machID%2==1:
        return 5
    elif machID<=NUM_MACH_IN_ZONE*3 and machID%2==0:
        return 6
    else:
        return None
    
def enhance_mes_by_nau(df:pd.DataFrame)->pd.Series:
    df_on_mach = df.copy()
    zero_mes_nau_by_mach = (
        df_on_mach.loc[(df_on_mach["Weight"] == 0) & (df_on_mach["NAU_prs"] > 0), ["MachID", "NAU_prs"]]
        .set_index("MachID")["NAU_prs"]
        .to_dict()
    )

    if zero_mes_nau_by_mach:
        logger.info("Replacing zero MES_prs with NAU_prs: %s", zero_mes_nau_by_mach)

    df_on_mach["MES_prs"] = df_on_mach["MES_prs"].where(
                                df_on_mach["Weight"] != 0,
                                df_on_mach["NAU_prs"] 
                            )
    return df_on_mach["MES_prs"]


def extract_base_data(extractor_cls: type[BaseExtractor], start_time:str, end_time:str, shift:int=0)->pd.DataFrame:
    config = AppConfig.from_env()
    ext = extractor_cls.from_config(config)

    start_dt = parse_start_date(start_time)
    end_dt = parse_start_date(end_time)

    if end_dt < start_dt:
        raise SystemExit("End date must be on or after the start date.")
    
    return ext.extract(start_dt, end_dt, shift)
