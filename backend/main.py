from fastapi import FastAPI
from backend.app.api.v1.auth import router as auth_router
from backend.app.database import create_db_and_tables

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    create_db_and_tables()

@app.get("/api/v1/health")
def read_root():
    return {"status": "ok"}

app.include_router(auth_router, prefix="/api/v1")

