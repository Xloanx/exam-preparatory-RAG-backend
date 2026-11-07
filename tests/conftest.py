import os

os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:OGlomon%40%40@127.0.0.1:5432/exam_prep_test"
os.environ["SECRET_KEY"] = "test-secret"

import pytest
import httpx
from httpx import ASGITransport, AsyncClient

from app.db import Base, engine
from app.main import app


@pytest.fixture
async def client():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    await engine.dispose()
