"""Health check endpoints."""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.redis import get_redis

router = APIRouter(prefix="/health", tags=["Health"])


class HealthStatus(BaseModel):
    """Health check response model."""

    status: str
    timestamp: str
    version: str
    environment: str
    checks: dict[str, Any]


class ComponentHealth(BaseModel):
    """Individual component health status."""

    status: str
    latency_ms: float | None = None
    error: str | None = None


async def check_database(db: AsyncSession) -> ComponentHealth:
    """Check database connectivity."""
    start = datetime.now(timezone.utc)
    try:
        await db.execute(text("SELECT 1"))
        latency = (datetime.now(timezone.utc) - start).total_seconds() * 1000
        return ComponentHealth(status="healthy", latency_ms=round(latency, 2))
    except Exception as e:
        return ComponentHealth(status="unhealthy", error=str(e))


async def check_redis(redis: Redis) -> ComponentHealth:
    """Check Redis connectivity."""
    start = datetime.now(timezone.utc)
    try:
        await redis.ping()
        latency = (datetime.now(timezone.utc) - start).total_seconds() * 1000
        return ComponentHealth(status="healthy", latency_ms=round(latency, 2))
    except Exception as e:
        return ComponentHealth(status="unhealthy", error=str(e))


@router.get("", response_model=HealthStatus)
async def health_check() -> HealthStatus:
    """
    Basic health check endpoint.
    
    Returns the application status without checking dependencies.
    """
    return HealthStatus(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        checks={},
    )


@router.get("/ready", response_model=HealthStatus)
async def readiness_check(
    db: AsyncSession = Depends(get_db),
) -> HealthStatus:
    """
    Readiness check endpoint.
    
    Checks all dependencies (database, redis) to determine if the
    application is ready to receive traffic.
    """
    checks: dict[str, Any] = {}
    overall_status = "healthy"
    
    # Check database
    db_health = await check_database(db)
    checks["database"] = db_health.model_dump(exclude_none=True)
    if db_health.status != "healthy":
        overall_status = "unhealthy"
    
    # Check Redis
    try:
        redis = get_redis()
        redis_health = await check_redis(redis)
        checks["redis"] = redis_health.model_dump(exclude_none=True)
        if redis_health.status != "healthy":
            overall_status = "degraded" if overall_status == "healthy" else overall_status
    except RuntimeError:
        checks["redis"] = {"status": "unhealthy", "error": "Redis not initialized"}
        overall_status = "degraded" if overall_status == "healthy" else overall_status
    
    return HealthStatus(
        status=overall_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        checks=checks,
    )


@router.get("/live")
async def liveness_check() -> dict[str, str]:
    """
    Liveness check endpoint.
    
    Simple endpoint to check if the application process is running.
    Used by container orchestrators for restart decisions.
    """
    return {"status": "alive"}
