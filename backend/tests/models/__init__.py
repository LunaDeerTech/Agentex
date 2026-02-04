"""Test models fixtures and configuration."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory


@pytest.fixture
async def db() -> AsyncSession:
    """Provide a database session for tests."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
