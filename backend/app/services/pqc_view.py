import pandas as pd
import numpy as np
from fastapi import HTTPException
from extractors import PQCExtractor
from app.services.utils import extract_base_data
from cores.constants import PQC_FREQ_THRESHOLD


def _extract_pqc_data(start_time:str, end_time:str, shift:int)->pd.DataFrame:
    df = extract_base_data(PQCExtractor, start_time, end_time, shift)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    df["Shift_Start_Time"] = pd.to_datetime(df["Date"].astype(str) + " " + df["Shift"].astype(str))
    df["Role"] = df["Role_Name"].str.split("-").str[0].str.strip()
    df["Name"] = df["Role_Name"].str.split("-").str[1].str.strip()
    df = df.drop(columns=["Date", "Shift", "Role_Name"])
    df["Style_Code"] = df["Style_Code"].apply(lambda x: x.strip().upper() if isinstance(x, str) and x.strip() else None)
    return df



def handle_pqc_view_by_sku(start_time:str, end_time:str, shift:int)->pd.DataFrame:
    df = _extract_pqc_data(start_time, end_time, shift)
    
    df = df.groupby(["Shift_Start_Time", "Style_Code"], as_index=False).agg(
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
    
    df = df.sort_values(["Shift_Start_Time"])
    df["Shift_Start_Time"] = df["Shift_Start_Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df = df.reset_index(names="id")
    return df


def handle_pqc_sku_detail(start_time:str, shift:int, style:str)->pd.DataFrame:
    df = _extract_pqc_data(start_time, start_time, shift)
    df = df[df["Style_Code"]==style]
    
    df = df.groupby(["Shift_Start_Time", "MachID"], as_index=False).agg(
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
    
    df = df.sort_values(["Shift_Start_Time"])
    df["Shift_Start_Time"] = df["Shift_Start_Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df = df.reset_index(names="id")
    return df


def handle_pqc_view_by_staff(start_time:str, end_time:str, shift:int)->pd.DataFrame:
    df = _extract_pqc_data(start_time, end_time, shift)
    if len(df)==0:
        return pd.DataFrame()
    
    df = df.groupby(["Shift_Start_Time", "Name", "Role"], as_index=False).agg(
        pqc_cnt=("MachID", "size"),
        start_check = ("DateRec", "min"),
        end_check = ("DateRec", "max"),
        avg_adj_diff=("DateRec", lambda x: x.sort_values().diff()[lambda s: s > pd.Timedelta(minutes=PQC_FREQ_THRESHOLD)].mean()),
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
    df = _extract_pqc_data(start_time, start_time, shift)
    df = df[df["Name"]==name]

    df = df[["DateRec", "MachID", "Style_Code", "toeHole", "brokenNDL", "missNDL", "fanYarn", "missYarn", "logoIssue", "dirty", "feisha", "other"]]
    df = df.sort_values(["DateRec"])
    df["DateRec"] = df["DateRec"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["Style_Code"] = df["Style_Code"].str.strip()
    df = df.reset_index(names="id")
    df = df.replace([np.nan, np.inf, -np.inf], None)
    return df


def merge_pqc_to_mach_dialog(df:pd.DataFrame, start_time:str, shift:int)->pd.DataFrame:
    if shift == 0:
        raise HTTPException(
            status_code=400,
            detail="shift can't be zero in mach dialog."
        )
    
    df_defect = _extract_pqc_data(start_time, start_time, shift)

    df_defect = df_defect.groupby(["MachID", "Style_Code"], as_index=False).agg(
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
    df_defect["defects"] = df_defect[["toeHole", "brokenNDL", "missNDL", "fanYarn", \
                        "missYarn", "logoIssue", "dirty", "feisha", "other"]].apply(lambda rec: sum(rec),axis=1)
    df_defect["defects"] = df_defect["defects"] // 2
    df_defect = df_defect[["MachID", "Style_Code", "defects", "pqc_cnt"]]
    df = df.merge(df_defect, on=["MachID", "Style_Code"], how="left")
    return df


def merge_pqc_to_shift_view(df:pd.DataFrame, start_time:str, end_time:str, shift:int)->pd.DataFrame:
    df_defect = _extract_pqc_data(start_time, end_time, shift)

    df_defect = df_defect.groupby(["Shift_Start_Time"], as_index=False).agg(
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
    df_defect["defects"] = df_defect[["toeHole", "brokenNDL", "missNDL", "fanYarn", \
                        "missYarn", "logoIssue", "dirty", "feisha", "other"]].apply(lambda rec: sum(rec),axis=1)
    df_defect["defects"] = df_defect["defects"] // 2
    df_defect = df_defect[["Shift_Start_Time", "defects", "pqc_cnt"]]
    df = df.merge(df_defect, on="Shift_Start_Time", how="left")
    return df


def merge_pqc_to_sku_view(df:pd.DataFrame, start_time:str, end_time:str, shift:int)->pd.DataFrame:
    df_defect = _extract_pqc_data(start_time, end_time, shift)
    df_defect["Style_Code"] = df_defect["Style_Code"].apply(lambda x: x.strip().split()[0].upper() if isinstance(x, str) and x.strip() else None)

    df_defect = df_defect.groupby(["Style_Code", "Shift_Start_Time"], as_index=False).agg(
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
    df_defect["defects"] = df_defect[["toeHole", "brokenNDL", "missNDL", "fanYarn", \
                        "missYarn", "logoIssue", "dirty", "feisha", "other"]].apply(lambda rec: sum(rec),axis=1)
    df_defect["defects"] = df_defect["defects"] // 2
    df_defect = df_defect[["Shift_Start_Time", "Style_Code", "defects", "pqc_cnt"]]
    
    df = df.merge(df_defect, on=["Style_Code", "Shift_Start_Time"], how="left")
    return df
