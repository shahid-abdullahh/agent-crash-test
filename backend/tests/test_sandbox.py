import pytest
import httpx


@pytest.mark.asyncio
async def test_sandbox_flight_search_and_filtering(async_client: httpx.AsyncClient):
    # List all flights
    resp = await async_client.get("/sandbox/flights")
    assert resp.status_code == 200
    flights = resp.json()
    assert len(flights) == 5

    # Filter by origin and destination
    resp_filtered = await async_client.get("/sandbox/flights?origin=DEL&destination=BOM")
    assert resp_filtered.status_code == 200
    del_bom_flights = resp_filtered.json()
    assert len(del_bom_flights) == 2
    assert all(f["origin"] == "DEL" and f["destination"] == "BOM" for f in del_bom_flights)

    # Filter with max_price
    resp_budget = await async_client.get("/sandbox/flights?origin=DEL&destination=BOM&max_price=8000")
    assert resp_budget.status_code == 200
    budget_flights = resp_budget.json()
    assert len(budget_flights) == 1
    assert budget_flights[0]["flight_id"] == "FL-101"
    assert budget_flights[0]["price"] == 6500.0


@pytest.mark.asyncio
async def test_sandbox_flight_details(async_client: httpx.AsyncClient):
    resp = await async_client.get("/sandbox/flights/FL-101")
    assert resp.status_code == 200
    flight = resp.json()
    assert flight["flight_id"] == "FL-101"
    assert flight["available_seats"] == 5

    # 404 for invalid flight
    resp_404 = await async_client.get("/sandbox/flights/FL-NONEXISTENT")
    assert resp_404.status_code == 404


@pytest.mark.asyncio
async def test_sandbox_reservation_mutates_state(async_client: httpx.AsyncClient):
    # Check initial seats
    flight_resp = await async_client.get("/sandbox/flights/FL-101")
    initial_seats = flight_resp.json()["available_seats"]

    # Book reservation
    payload = {
        "flight_id": "FL-101",
        "passenger_name": "Aditi Roy",
    }
    book_resp = await async_client.post("/sandbox/reservations", json=payload)
    assert book_resp.status_code == 200
    reservation = book_resp.json()
    assert reservation["reservation_id"].startswith("RES-")
    assert reservation["passenger_name"] == "Aditi Roy"
    assert reservation["status"] == "confirmed"

    # Verify seats decreased
    updated_flight_resp = await async_client.get("/sandbox/flights/FL-101")
    assert updated_flight_resp.json()["available_seats"] == initial_seats - 1

    # Verify sandbox state snapshot
    state_resp = await async_client.get("/sandbox/state")
    assert state_resp.status_code == 200
    state_data = state_resp.json()
    assert state_data["total_reservations"] == 1
    assert state_data["flight_seats"]["FL-101"] == initial_seats - 1
