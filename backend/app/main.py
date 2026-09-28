from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import router
from app.db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.app_env == "development":
        init_db()
    yield

app = FastAPI(title="SEV API", version="1.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router, prefix="/api/v1")

@app.get("/api/v1/health")
def health():
    return {"status": "ok", "service": "sev-api", "version": "1.1.0"}

@app.get("/api/v1/readiness")
def readiness():
    return {"status": "ready", "demo_mode": settings.demo_mode, "database": "configured", "providers": {"notam": "on-demand", "metar": "on-demand"}}
