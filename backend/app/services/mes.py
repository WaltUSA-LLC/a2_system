from nautilus_mes_base import AppConfig
from nautilus_mes_base import MESOrchestra
from nautilus_mes_base.utils import parse_start_date
import pandas as pd

def handle_weight_data(start_time:str, end_time:str)->pd.DataFrame:
    config = AppConfig.from_env()
    mes = MESOrchestra.from_config(config)

    start_dt = parse_start_date(start_time)
    end_dt = parse_start_date(end_time)

    if end_dt < start_dt:
        raise SystemExit("End date must be on or after the start date.")
    
    df = mes.generate_mes(start_dt, end_dt)
    df["Shift_Start_Time"] = df["Shift_Start_Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df = df.reset_index(names="id")
    df = df.astype(object).where(pd.notnull(df), None)
    return df




