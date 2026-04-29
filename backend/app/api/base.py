from fastapi import APIRouter
from app.services.mach_view import handle_mach_view
from app.services.sku_view import handle_sku_view
from app.services.shift_view import handle_shift_view
from app.services.stop_view import handle_stop_view_by_code
from app.services.stop_view import handle_stop_view_by_mach
from app.services.stop_view import handle_stop_mach_detail
from app.services.stop_view import handle_stop_code_detail
import pandas as pd

router = APIRouter()

@router.get("/mach")
def get_mes(start:str, end:str, shift: int):
    df = handle_mach_view(start, end, shift)
    return {"content": df.to_dict(orient="records")}

@router.get("/shift")
def get_shift(start:str, end:str, shift: int):
    df = handle_shift_view(start, end, shift)
    return {"content": df.to_dict(orient="records")}

@router.get("/sku")
def get_sku(start:str, end:str, shift: int):
    df = handle_sku_view(start, end, shift)
    return {"content": df.to_dict(orient="records")}

@router.get("/stop/code")
def get_stop_by_code(start:str, end:str, shift: int):
    df, df_freq, df_mach, df_dur_sum, df_dur_med = handle_stop_view_by_code(start, end, shift)
    return {"content": df.to_dict(orient="records"),
            "chart_freq": df_freq.to_dict(orient="records"),
            "chart_mach": df_mach.to_dict(orient="records"),
            "chart_dur_sum": df_dur_sum.to_dict(orient="records"),
            "chart_dur_med": df_dur_med.to_dict(orient="records")}

@router.get("/stop/mach")
def get_stop_by_mach(start:str, end:str, shift: int):
    df_table, df_chart = handle_stop_view_by_mach(start, end, shift)
    return {"content": df_table.to_dict(orient="records"),
            "chart": df_chart.to_dict(orient="records")}

@router.get("/stop/mach/detail")
def get_stop_by_mach_detail(start:str, end:str, shift: int, mach: int, style: str):
    df = handle_stop_mach_detail(start, end, shift, mach, style)
    return {"content": df.to_dict(orient="records")}

@router.get("/stop/code/detail")
def get_stop_by_code_detail(start:str, end:str, shift: int, stop_code:int):
    df = handle_stop_code_detail(start, end, shift, stop_code)
    return {"content": df.to_dict(orient="records")}