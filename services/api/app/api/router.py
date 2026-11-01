from fastapi import APIRouter
from app.api.routes import system, auth, characters, conversations, admin

api_router = APIRouter()
api_router.include_router(system.router, tags=["system"])
api_router.include_router(auth.router, tags=["authentication"])
api_router.include_router(characters.router, tags=["characters"])
api_router.include_router(conversations.router, tags=["conversations"])
api_router.include_router(admin.router, tags=["administration"])
