from fastapi import APIRouter
from app.services.mach_view import handle_mach_view
from app.services.sku_view import handle_sku_view

router = APIRouter()

@router.get("/mach")
def get_mes(start:str, end:str, shift: int):
    df = handle_mach_view(start, end, shift)
    return {"content": df.to_dict(orient="records")}

@router.get("/sku")
def get_sku_by(start:str, end:str, shift: int):
    df = handle_sku_view(start, end, shift)
    return {"content": df.to_dict(orient="records")}

'''@router.get("/nau/time")
def get_nau_time(start:str, end:str):
    df = handle_nau_time_data(start, end)
    return {"columns": [{ "field": col, "headerName": col, "width": 130, "align": 'center', "headerAlign": 'center', } for col in df.columns.to_list()],
            "content": df.to_dict(orient="records")}

@router.get("/nau/stop")
def get_nau_stop(start:str, end:str):
    df = handle_nau_stop_data(start, end)
    return {"columns": [{ "field": col, "headerName": col, "width": 130, "align": 'center', "headerAlign": 'center', } for col in df.columns.to_list()],
            "content": df.to_dict(orient="records")}'''