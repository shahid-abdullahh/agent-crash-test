import pytest
import pytest_asyncio
import httpx
from app.main import app
from app.sandbox.state import sandbox_state
from app.services.repository import task_repository, run_repository


@pytest.fixture(autouse=True)
def reset_all_state():
    sandbox_state.reset()
    # Reset in-memory run repository between tests for deterministic isolation
    run_repository._runs.clear()
    yield
    sandbox_state.reset()
    run_repository._runs.clear()


@pytest_asyncio.fixture
async def async_client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
