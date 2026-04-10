from fastapi import FastAPI
from api.base import router as base

app = FastAPI()

app.include_router(base, prefix="/base")

@app.get("/")
def read_root():
    return {"Hello": "World"}
