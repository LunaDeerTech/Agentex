"""API v1 router initialization."""

from fastapi import APIRouter

from app.api.v1 import auth, users

api_router = APIRouter(prefix="/v1")

# Include sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
