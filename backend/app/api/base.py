from fastapi import APIRouter
from app.services.mach_view import handle_mach_view
from app.services.sku_view import handle_sku_view
from app.services.stop_view import handle_stop_view
router = APIRouter()

@router.get("/mach")
def get_mes(start:str, end:str, shift: int):
    df = handle_mach_view(start, end, shift)
    return {"content": df.to_dict(orient="records")}

@router.get("/sku")
def get_sku(start:str, end:str, shift: int):
    df = handle_sku_view(start, end, shift)
    return {"content": df.to_dict(orient="records")}

@router.get("/stop")
def get_stop(start:str, end:str, shift: int):
    df = handle_stop_view(start, end, shift)
    return {"content": df.to_dict(orient="records")}
