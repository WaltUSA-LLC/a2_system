from nautilus_mes_base import AppConfig
from nautilus_mes_base import MESOrchestra
from nautilus_mes_base.utils import parse_start_date
from app.services.utils import estimate_st_output_prs
import pandas as pd
import numpy as np


def handle_sku_view(start_time:str, end_time:str, shift:int)->pd.DataFrame:
    config = AppConfig.from_env()
    mes_nau = MESOrchestra.from_config(config)

    start_dt = parse_start_date(start_time)
    end_dt = parse_start_date(end_time)

    if end_dt < start_dt:
        raise SystemExit("End date must be on or after the start date.")
    
    df = mes_nau.generate_mes(start_dt, end_dt, shift)
    print(len(df))
    print(type(df["Shift_Start_Time"].iloc[0]))
    df["Style_Code"] = df["Style_Code"].apply(lambda x: x.strip().split()[0] if isinstance(x, str) and x.strip() else None)
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
    return df_sku