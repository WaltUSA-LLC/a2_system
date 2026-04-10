from fastapi import APIRouter
from app.services.mes import get_weights

router = APIRouter()

@router.get("/mes")
def get_mes_data(start:str, end:str):
    df = get_weights(start, end)
    return {"columns": [{ "field": col, "headerName": col, "width": 130 } for col in df.columns.to_list()],
            "content": df.to_dict(orient="records")}