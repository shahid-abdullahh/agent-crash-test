from fastapi import APIRouter, Query
from typing import List, Optional
from app.sandbox.models import (
    Flight,
    Reservation,
    ReservationCreateRequest,
    ScenarioConfig,
    SandboxStateSnapshot,
)
from app.sandbox.state import sandbox_state

router = APIRouter(prefix="/sandbox", tags=["Sandbox Travel API"])


@router.get("/flights", response_model=List[Flight])
def list_flights(
    origin: Optional[str] = Query(None, description="Flight origin airport code, e.g. DEL"),
    destination: Optional[str] = Query(None, description="Flight destination airport code, e.g. BOM"),
    max_price: Optional[float] = Query(None, description="Maximum flight price in INR"),
):
    """Search and filter available flights in the sandbox."""
    return sandbox_state.search_flights(origin=origin, destination=destination, max_price=max_price)


@router.get("/flights/{flight_id}", response_model=Flight)
def get_flight(flight_id: str):
    """Get flight details by ID."""
    return sandbox_state.get_flight(flight_id)


@router.post("/reservations", response_model=Reservation)
def create_reservation(payload: ReservationCreateRequest):
    """Create a new flight reservation."""
    return sandbox_state.create_reservation(payload)


@router.get("/reservations/{reservation_id}", response_model=Reservation)
def get_reservation(reservation_id: str):
    """Get reservation details by reservation ID."""
    return sandbox_state.get_reservation(reservation_id)


@router.get("/state", response_model=SandboxStateSnapshot)
def get_sandbox_state():
    """Directly inspect sandbox state for verification & evaluation."""
    return sandbox_state.get_snapshot()


@router.post("/reset")
def reset_sandbox():
    """Reset sandbox to clean initial state."""
    sandbox_state.reset()
    return {"status": "reset", "message": "Sandbox state has been restored to default"}


@router.post("/configure")
def configure_scenario(config: ScenarioConfig):
    """Configure active fault injection scenario."""
    sandbox_state.configure_scenario(config)
    return {"status": "configured", "scenario": config}
