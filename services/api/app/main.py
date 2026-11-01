from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.router import api_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Initialize external resources in dedicated lifespan modules as they are implemented.
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="ALAP AI Companion platform API",
    lifespan=lifespan,
    docs_url="/docs" if settings.app_env != "production" else None,
    redoc_url=None,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health/live", tags=["health"])
async def liveness() -> dict[str, str]:
    return {"status": "alive"}


@app.get("/health/ready", tags=["health"])
async def readiness() -> dict[str, str]:
    # Replace with real DB/Redis/provider dependency checks before production.
    return {"status": "ready", "dependencies": "not-yet-verified"}
