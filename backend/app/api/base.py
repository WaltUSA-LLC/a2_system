from fastapi import APIRouter
from app.services.mes import get_weights

router = APIRouter()

@router.get("/mes")
def get_mes_data():
    df = get_weights("2026-03-16", "2026-03-16")
    print(df.head())
    return {"columns": [{ "field": col, "headerName": col, "width": 130 } for col in df.columns.to_list()],
            "content": df.to_dict(orient="records")}