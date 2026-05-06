from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.base import router as base

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174",
                   "http://localhost:5173",
                   "http://127.0.0.1:5173",
                   "http://10.0.20.245:5173",
                   "http://100.85.38.28:5173",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(base, prefix="/base")

@app.get("/")
def read_root():
    return {"Hello": "World"}
