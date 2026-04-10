from nautilus_mes_base import AppConfig
from nautilus_mes_base import NAUTimeOrchestra
from nautilus_mes_base.utils import parse_start_date
import pandas as pd

def get_nau_time(start_time:str, end_time:str)->pd.DataFrame:
    config = AppConfig.from_env()
    nau_run = NAUTimeOrchestra.from_config(config)

    start_dt = parse_start_date(start_time)
    end_dt = parse_start_date(end_time)

    if end_dt < start_dt:
        raise SystemExit("End date must be on or after the start date.")
    
    df = nau_run.generate_nau_time(start_dt, end_dt)
    df["shift_start_time"] = df["shift_start_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df = df.reset_index(names="id")
    df = df.astype(object).where(pd.notnull(df), None)
    return df




