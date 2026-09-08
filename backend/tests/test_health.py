import pytest
import httpx


@pytest.mark.asyncio
async def test_health_check(async_client: httpx.AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "timestamp" in data
