import pandas as pd
import numpy as np
from extractors import PQCExtractor
from app.services.utils import extract_base_data

def handle_pqc_view_by_staff(start_time:str, end_time:str, shift:int)->pd.DataFrame:
    df = extract_base_data(PQCExtractor, start_time, end_time, shift)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    df["Shift_Start_Time"] = pd.to_datetime(df["Date"].astype(str) + " " + df["Shift"].astype(str))
    df["Name"] = df["Name"].str.split("-").str[1].str.strip()
    df = df.drop(columns=["Date", "Shift"])
    
    df = df.groupby(["Shift_Start_Time", "Name"], as_index=False).agg(
        pqc_cnt=("MachID", "size"),
        start_check = ("DateRec", "min"),
        end_check = ("DateRec", "max"),
        avg_adj_diff=("DateRec", lambda x: x.sort_values().diff().mean()),
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
    df["start_check"] = df["start_check"].dt.strftime("%H:%M:%S")
    df["end_check"] = df["end_check"].dt.strftime("%H:%M:%S")
    
    df = df.sort_values(["Shift_Start_Time"])
    df["Shift_Start_Time"] = df["Shift_Start_Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df = df.reset_index(names="id")
    return df


def handle_pqc_view_by_staff_detail(start_time:str, shift:int, name:str)->pd.DataFrame:
    df = extract_base_data(PQCExtractor, start_time, start_time, shift)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    df["Shift_Start_Time"] = pd.to_datetime(df["Date"].astype(str) + " " + df["Shift"].astype(str))
    df["Name"] = df["Name"].str.split("-").str[1].str.strip()
    df = df.drop(columns=["Date", "Shift"])
    df = df[df["Name"]==name]

    df = df[["DateRec", "MachID", "Style_Code", "toeHole", "brokenNDL", "missNDL", "fanYarn", "missYarn", "logoIssue", "dirty", "feisha", "other"]]
    df = df.sort_values(["DateRec"])
    df["DateRec"] = df["DateRec"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["Style_Code"] = df["Style_Code"].str.strip()
    df = df.reset_index(names="id")
    return df


def handle_pqc_mach_detail(start_time:str, end_time:str, shift:int)->pd.DataFrame:
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