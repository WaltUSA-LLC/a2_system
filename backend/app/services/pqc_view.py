import pandas as pd
import numpy as np
from extractors import PQCExtractor
from app.services.utils import extract_base_data

def handle_pqc_view(start_time:str, end_time:str, shift:int):
    df = extract_base_data(PQCExtractor, start_time, end_time, shift)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    df["Shift_Start_Time"] = pd.to_datetime(df["Date"].astype(str) + " " + df["Shift"].astype(str))
    df["Name"] = df["Name"].str.split("-").str[1].str.strip()
    df = df.drop(columns=["Date", "Shift"])

    df = df.groupby(["Shift_Start_Time", "MachID", "Style_Code"], as_index=False).agg(
        pqc_cnt=("MachID", "size"),
        toeHole=("toeHole", "sum"),
        brokenNDL=("brokenNDL", "sum"),
        missNDL=("missNDL", "sum"),
        fanYarn=("fanYarn", "sum"),
        missYarn=("missYarn", "sum"),
        logoIssue=("logoIssue", "sum"),
        dirty=("dirty", "sum"),
        feisha=("feisha", "sum"),
        other=("other", "sum")
    )
    df["defects"] = df[["toeHole", "brokenNDL", "missNDL", "fanYarn", \
                        "missYarn", "logoIssue", "dirty", "feisha", "other"]].apply(lambda rec: sum(rec),axis=1)

    df = df.sort_values(["Shift_Start_Time", "MachID"])
    df["Shift_Start_Time"] = df["Shift_Start_Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df = df.reset_index(names="id")
    return df