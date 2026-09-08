from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum
from datetime import datetime


class ScenarioMode(str, Enum):
    NORMAL = "normal"
    TIMEOUT_AFTER_COMMIT = "timeout_after_commit"


class ScenarioConfig(BaseModel):
    mode: ScenarioMode = ScenarioMode.NORMAL
    target_endpoint: str = "/reservations"
    fail_first_n_attempts: int = 1
    attempts_seen: int = 0


class Flight(BaseModel):
    flight_id: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    price: float
    currency: str = "INR"
    available_seats: int
    total_seats: int


class ReservationStatus(str, Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class ReservationCreateRequest(BaseModel):
    flight_id: str
    passenger_name: str
    idempotency_key: Optional[str] = None


class Reservation(BaseModel):
    reservation_id: str
    flight_id: str
    passenger_name: str
    status: ReservationStatus = ReservationStatus.CONFIRMED
    price_paid: float
    created_at: str
    idempotency_key: Optional[str] = None


class SandboxStateSnapshot(BaseModel):
    scenario: ScenarioConfig
    total_reservations: int
    reservations: List[Reservation]
    flight_seats: Dict[str, int]
