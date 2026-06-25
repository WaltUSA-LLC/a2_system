from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.sku_view import handle_sku_view, handle_sku_mach_detail
from app.services.shift_view import handle_shift_view, handle_shift_mach_detail
from app.services.stop_view import handle_stop_view_by_code
from app.services.stop_view import handle_stop_view_by_mach
from app.services.stop_view import handle_stop_mach_detail
from app.services.stop_view import handle_stop_code_detail
from app.services.staff_info import fetch_staff_info_by_date_and_shift
from app.services.staff_schedule import upload_staff_schedule
from app.services.pqc_view import handle_pqc_view_by_staff,\
    handle_pqc_view_by_staff_in_period, \
    handle_pqc_view_by_staff_detail,\
    handle_pqc_view_by_sku,\
    handle_pqc_sku_detail

router = APIRouter()


@router.get("/shift")
def get_shift(start:str, end:str, shift: int):
    df = handle_shift_view(start, end, shift)
    return {"content": df.to_dict(orient="records")}


@router.get("/shift/detail")
def get_shift_detail(start:str, shift: int):
    df = handle_shift_mach_detail(start, shift)
    df_staff = fetch_staff_info_by_date_and_shift(start, shift)
    return {"content": df.to_dict(orient="records"),
            "staff": df_staff.to_dict(orient="records")}

@router.get("/sku")
def get_sku(start:str, end:str, shift: int):
    df = handle_sku_view(start, end, shift)
    return {"content": df.to_dict(orient="records")}

@router.get("/sku/detail")
def get_sku_detail(start:str, end:str, shift: int, style:str):
    df = handle_sku_mach_detail(start, end, shift, style)
    df_staff = fetch_staff_info_by_date_and_shift(start, shift)
    return {"content": df.to_dict(orient="records"),
            "staff": df_staff.to_dict(orient="records")}

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

@router.get("/pqc/staff")
def get_pqc_staff(start:str, end:str, shift: int):
    df = handle_pqc_view_by_staff(start, end, shift)
    return {"content": df.to_dict(orient="records")}

@router.get("/pqc/staff/period")
def get_pqc_staff_in_period(start:str, end:str):
    df = handle_pqc_view_by_staff_in_period(start, end)
    return {"content": df.to_dict(orient="records")}

@router.get("/pqc/staff/detail")
def get_pqc_staff_detail(start:str, shift: int, name: str):
    df = handle_pqc_view_by_staff_detail(start, shift, name)
    return {"content": df.to_dict(orient="records")}

@router.get("/pqc/sku")
def get_pqc_sku(start:str, end:str, shift: int):
    df = handle_pqc_view_by_sku(start, end, shift)
    return {"content": df.to_dict(orient="records")}

@router.get("/pqc/sku/detail")
def get_pqc_sku_detail(start:str, shift: int, style:str):
    df = handle_pqc_sku_detail(start, shift, style)
    return {"content": df.to_dict(orient="records")}


@router.post("/uploads/staff")
async def upload_knit_schedule(
    file: UploadFile = File(...),
    year: int = Form(...),
    month: int = Form(...),
):
    try:
        result = await upload_staff_schedule(
            file=file,
            year=year,
            month=month,
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=400,
            detail=f"File error: {str(e)}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to import knit schedule: {str(e)}",
        )