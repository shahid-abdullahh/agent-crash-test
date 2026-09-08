import pytest
import httpx
from app.main import app
from app.services.integration_service import integration_service
from app.services.documentation_service import documentation_service
from app.schemas.integration import IntegrationCreateRequest


@pytest.mark.asyncio
async def test_integrations_and_connectors_api(async_client: httpx.AsyncClient):
    # 1. List integrations
    res = await async_client.get("/integrations")
    assert res.status_code == 200
    integrations = res.json()
    assert len(integrations) >= 1
    int_id = integrations[0]["id"]

    # 2. Get specific integration
    res = await async_client.get(f"/integrations/{int_id}")
    assert res.status_code == 200
    int_data = res.json()
    assert int_data["id"] == int_id
    assert len(int_data["operations"]) >= 4
    assert len(int_data["readiness_findings"]) >= 1

    # 3. Generate Integration code
    res = await async_client.get(f"/integrations/{int_id}/code")
    assert res.status_code == 200
    code_pkg = res.json()
    assert "client.py" in code_pkg
    assert "README.md" in code_pkg
    assert "tools.json" in code_pkg

    # 4. List Connectors
    res = await async_client.get("/connectors")
    assert res.status_code == 200
    connectors = res.json()
    assert len(connectors) >= 1

    # 5. Documentation generation
    res = await async_client.get(f"/documentation/{int_id}")
    assert res.status_code == 200
    doc_data = res.json()
    assert doc_data["integration_id"] == int_id
    assert len(doc_data["endpoints"]) >= 4
    assert "API Usage Documentation" in doc_data["markdown_content"]


@pytest.mark.asyncio
async def test_payments_multi_service_endpoint(async_client: httpx.AsyncClient):
    # 1. Create a reservation first
    res = await async_client.post("/sandbox/reservations", json={
        "flight_id": "FL-101",
        "passenger_name": "Multi Service Tester",
        "idempotency_key": "IDEM-PAY-TEST-001"
    })
    assert res.status_code == 200
    reservation = res.json()
    res_id = reservation["reservation_id"]

    # 2. Process payment for reservation
    res = await async_client.post("/sandbox/payments", json={
        "reservation_id": res_id,
        "amount": 6500.0,
        "payment_method": "CARD",
        "idempotency_key": "PAY-IDEM-001"
    })
    assert res.status_code == 200
    payment = res.json()
    assert payment["reservation_id"] == res_id
    assert payment["status"] == "completed"

    # 3. Repeat payment with same idempotency key -> Returns same transaction without duplicate
    res = await async_client.post("/sandbox/payments", json={
        "reservation_id": res_id,
        "amount": 6500.0,
        "payment_method": "CARD",
        "idempotency_key": "PAY-IDEM-001"
    })
    assert res.status_code == 200
    payment_dup = res.json()
    assert payment_dup["payment_id"] == payment["payment_id"]
