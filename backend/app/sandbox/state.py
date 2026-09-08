import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from fastapi import HTTPException
from app.sandbox.models import (
    Flight,
    Reservation,
    ReservationCreateRequest,
    ReservationStatus,
    ScenarioConfig,
    ScenarioMode,
    SandboxStateSnapshot,
)


def get_default_flights() -> Dict[str, Flight]:
    flights = [
        Flight(
            flight_id="FL-101",
            origin="DEL",
            destination="BOM",
            departure_time="2026-10-01T08:00:00Z",
            arrival_time="2026-10-01T10:15:00Z",
            price=6500.0,
            currency="INR",
            available_seats=5,
            total_seats=5,
        ),
        Flight(
            flight_id="FL-102",
            origin="DEL",
            destination="BOM",
            departure_time="2026-10-01T12:00:00Z",
            arrival_time="2026-10-01T14:15:00Z",
            price=9200.0,
            currency="INR",
            available_seats=10,
            total_seats=10,
        ),
        Flight(
            flight_id="FL-103",
            origin="DEL",
            destination="BLR",
            departure_time="2026-10-01T09:00:00Z",
            arrival_time="2026-10-01T11:45:00Z",
            price=7800.0,
            currency="INR",
            available_seats=3,
            total_seats=3,
        ),
        Flight(
            flight_id="FL-104",
            origin="DEL",
            destination="BLR",
            departure_time="2026-10-01T16:00:00Z",
            arrival_time="2026-10-01T18:45:00Z",
            price=11500.0,
            currency="INR",
            available_seats=8,
            total_seats=8,
        ),
        Flight(
            flight_id="FL-105",
            origin="DEL",
            destination="GOI",
            departure_time="2026-10-01T06:30:00Z",
            arrival_time="2026-10-01T09:00:00Z",
            price=5400.0,
            currency="INR",
            available_seats=2,
            total_seats=2,
        ),
    ]
    return {f.flight_id: f for f in flights}


class SandboxState:
    def __init__(self):
        self.flights: Dict[str, Flight] = get_default_flights()
        self.reservations: Dict[str, Reservation] = {}
        self.scenario: ScenarioConfig = ScenarioConfig()
        self.history: List[dict] = []

    def reset(self):
        self.flights = get_default_flights()
        self.reservations = {}
        self.scenario = ScenarioConfig()
        self.history = []

    def configure_scenario(self, config: ScenarioConfig):
        self.scenario = config

    def search_flights(
        self,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        max_price: Optional[float] = None,
    ) -> List[Flight]:
        results = list(self.flights.values())
        if origin:
            results = [f for f in results if f.origin.upper() == origin.upper()]
        if destination:
            results = [f for f in results if f.destination.upper() == destination.upper()]
        if max_price is not None:
            results = [f for f in results if f.price <= max_price]
        return sorted(results, key=lambda f: f.price)

    def get_flight(self, flight_id: str) -> Flight:
        if flight_id not in self.flights:
            raise HTTPException(status_code=404, detail=f"Flight {flight_id} not found")
        return self.flights[flight_id]

    def create_reservation(self, req: ReservationCreateRequest) -> Reservation:
        if req.flight_id not in self.flights:
            raise HTTPException(status_code=404, detail=f"Flight {req.flight_id} not found")

        flight = self.flights[req.flight_id]

        # Check idempotency key if provided
        if req.idempotency_key:
            for existing in self.reservations.values():
                if existing.idempotency_key == req.idempotency_key:
                    return existing

        if flight.available_seats <= 0:
            raise HTTPException(status_code=400, detail=f"No seats available on flight {req.flight_id}")

        # Failure Injection Check: INVALID_PARAMETER (Validation error occurs before state commit)
        if self.scenario.mode == ScenarioMode.INVALID_PARAMETER:
            if self.scenario.attempts_seen < self.scenario.fail_first_n_attempts:
                self.scenario.attempts_seen += 1
                raise HTTPException(
                    status_code=422,
                    detail="Validation Error: Invalid passenger name format (special characters or unverified prefix rejected by carrier API)."
                )

        # Commit reservation in server state
        flight.available_seats -= 1
        res_id = f"RES-{len(self.reservations) + 1:04d}"
        now_str = datetime.now(timezone.utc).isoformat()
        reservation = Reservation(
            reservation_id=res_id,
            flight_id=req.flight_id,
            passenger_name=req.passenger_name,
            status=ReservationStatus.CONFIRMED,
            price_paid=flight.price,
            created_at=now_str,
            idempotency_key=req.idempotency_key,
        )
        self.reservations[res_id] = reservation

        self.history.append({
            "action": "create_reservation",
            "reservation_id": res_id,
            "flight_id": req.flight_id,
            "passenger_name": req.passenger_name,
            "timestamp": now_str,
        })

        # Failure Injection Check: TIMEOUT_AFTER_COMMIT
        if self.scenario.mode == ScenarioMode.TIMEOUT_AFTER_COMMIT:
            if self.scenario.attempts_seen < self.scenario.fail_first_n_attempts:
                self.scenario.attempts_seen += 1
                # The state mutation has already happened (reservation created and seat decremented)
                # Now raise HTTP 504 Gateway Timeout simulating network/server drop after commit
                raise HTTPException(
                    status_code=504,
                    detail="Gateway Timeout: Upstream response timed out after processing operation"
                )

        return reservation

    def get_reservation(self, reservation_id: str) -> Reservation:
        if reservation_id not in self.reservations:
            raise HTTPException(status_code=404, detail=f"Reservation {reservation_id} not found")
        return self.reservations[reservation_id]

    def get_snapshot(self) -> SandboxStateSnapshot:
        return SandboxStateSnapshot(
            scenario=self.scenario,
            total_reservations=len(self.reservations),
            reservations=list(self.reservations.values()),
            flight_seats={f_id: f.available_seats for f_id, f in self.flights.items()},
        )


sandbox_state = SandboxState()
