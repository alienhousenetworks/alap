from fastapi import APIRouter
from app.api.routes import system, auth

api_router = APIRouter()
api_router.include_router(system.router, tags=["system"])
api_router.include_router(auth.router, tags=["authentication"])
