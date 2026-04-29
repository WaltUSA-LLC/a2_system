import math
import pandas as pd
import numpy as np

from extractors import AppConfig
from extractors import BaseExtractor
from extractors.utils import parse_start_date

def validate_throughput(rec:pd.Series) -> pd.Series:
    nau = rec["NAU_prs"]
    weight = rec["MES_prs"]
    on_time = rec["ON_Time"]
    avg_cycle = rec["Avg_Cycle"]
    discard = rec["Discard_prs"]
    theory_expect = math.ceil(on_time/avg_cycle/2) if not pd.isna(avg_cycle) else np.nan
    act_expect = theory_expect - discard if not pd.isna(theory_expect) else np.nan
    buffer = 10
    
    if (nau==0 and on_time==0) or (weight==0 and on_time==0):
        return 0
    if (weight<0 or weight>theory_expect+buffer or pd.isna(weight)) and (nau<0 or nau>theory_expect+buffer or pd.isna(nau)):
        return np.nan
    elif (weight<0 or weight>theory_expect+buffer or pd.isna(weight)):
        return nau
    else:
        return weight
    
    
def estimate_st_output_prs(rec: pd.Series) -> int:
    if pd.isna(rec["Avg_Cycle"]):
        return np.nan
    return math.floor((rec["ON_Time"]+rec["OFF_Time"])/rec["Avg_Cycle"]/2)


def clean_weight(df: pd.DataFrame) -> pd.DataFrame:
        cleaned_df = df.copy()
        if "Weight" in cleaned_df.columns:
            mask = (cleaned_df["Weight"] > 0) & (cleaned_df["Weight"] < 1)
            cleaned_df.loc[mask, "Weight"] = 0
        return cleaned_df

def extract_base_data(extractor_cls: type[BaseExtractor], start_time:str, end_time:str, shift:int=0)->pd.DataFrame:
    config = AppConfig.from_env()
    ext = extractor_cls.from_config(config)

    start_dt = parse_start_date(start_time)
    end_dt = parse_start_date(end_time)

    if end_dt < start_dt:
        raise SystemExit("End date must be on or after the start date.")
    
    return ext.extract(start_dt, end_dt, shift)