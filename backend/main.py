from fastapi import FastAPI
from backend.app.api.v1.auth import router as auth_router

app = FastAPI()

@app.get("/api/v1/health")
def read_root():
    return {"status": "ok"}

app.include_router(auth_router, prefix="/api/v1")

