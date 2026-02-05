"""API v1 router initialization."""

from fastapi import APIRouter

from app.api.v1 import agent, auth, models, sessions, users

api_router = APIRouter(prefix="/v1")

# Include sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(models.router, prefix="/models", tags=["LLM Models"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
api_router.include_router(agent.router, prefix="/agent", tags=["Agent"])
