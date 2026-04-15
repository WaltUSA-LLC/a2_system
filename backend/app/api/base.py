from fastapi import APIRouter
from app.services.mach_view import handle_mach_view
from app.services.nau import handle_nau_time_data
from app.services.nau import handle_nau_stop_data

router = APIRouter()

@router.get("/mes")
def get_mes(start:str, end:str):
    df = handle_mach_view(start, end)
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