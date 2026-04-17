from nautilus_mes_base import AppConfig
from nautilus_mes_base import NAUStopOrchestra
from nautilus_mes_base.utils import parse_start_date
import pandas as pd


def handle_stop_view(start_time:str, end_time:str)->pd.DataFrame:
    config = AppConfig.from_env()
    nau_stop = NAUStopOrchestra.from_config(config)

    start_dt = parse_start_date(start_time)
    end_dt = parse_start_date(end_time)

    if end_dt < start_dt:
        raise SystemExit("End date must be on or after the start date.")
    
    df = nau_stop.generate_nau_stop(start_dt, end_dt)
    #df["Recover_time"] = df["Recover_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    #df["Stop_time"] = df["Stop_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["Description"] = df["Description"].str.strip()
    df = df.reset_index(names="id")
    df = df.astype(object).where(pd.notnull(df), None)
    return df




