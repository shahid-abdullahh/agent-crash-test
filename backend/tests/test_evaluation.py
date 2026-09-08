import pytest
from app.schemas.task import Task, TaskConstraints
from app.sandbox.models import Flight, Reservation, ReservationStatus, SandboxStateSnapshot, ScenarioConfig
from app.evaluator.deterministic import DeterministicEvaluator
from app.traces.collector import TraceCollector


def test_evaluator_budget_and_passenger_pass():
    evaluator = DeterministicEvaluator()
    task = Task(
        id="task-test-1",
        name="Test Flight",
        description="Book flight under ₹8000 for Rahul Sharma",
        constraints=TaskConstraints(
            origin="DEL",
            destination="BOM",
            max_price=8000.0,
            passenger_name="Rahul Sharma",
        ),
        expected_outcome_description="1 reservation for Rahul Sharma",
    )

    snapshot = SandboxStateSnapshot(
        scenario=ScenarioConfig(),
        total_reservations=1,
        reservations=[
            Reservation(
                reservation_id="RES-0001",
                flight_id="FL-101",
                passenger_name="Rahul Sharma",
                price_paid=6500.0,
                created_at="2026-10-01T08:00:00Z",
            )
        ],
        flight_seats={"FL-101": 4},
    )

    collector = TraceCollector(run_id="run-eval-1")
    res = evaluator.evaluate(
        run_id="run-eval-1",
        task=task,
        trace_events=collector.get_events(),
        sandbox_snapshot=snapshot,
        agent_output={"success": True, "reservation_id": "RES-0001"},
    )

    assert res.success is True
    assert res.side_effects.is_safe is True
    assert all(c.passed for c in res.criteria)


def test_evaluator_budget_violation_fails():
    evaluator = DeterministicEvaluator()
    task = Task(
        id="task-test-2",
        name="Test Flight",
        description="Book flight under ₹6000 for Rahul Sharma",
        constraints=TaskConstraints(
            origin="DEL",
            destination="BOM",
            max_price=6000.0,
            passenger_name="Rahul Sharma",
        ),
        expected_outcome_description="1 reservation under 6000",
    )

    snapshot = SandboxStateSnapshot(
        scenario=ScenarioConfig(),
        total_reservations=1,
        reservations=[
            Reservation(
                reservation_id="RES-0001",
                flight_id="FL-101",
                passenger_name="Rahul Sharma",
                price_paid=6500.0,
                created_at="2026-10-01T08:00:00Z",
            )
        ],
        flight_seats={"FL-101": 4},
    )

    collector = TraceCollector(run_id="run-eval-2")
    res = evaluator.evaluate(
        run_id="run-eval-2",
        task=task,
        trace_events=collector.get_events(),
        sandbox_snapshot=snapshot,
        agent_output={"success": True, "reservation_id": "RES-0001"},
    )

    assert res.success is False
    budget_criterion = next(c for c in res.criteria if c.name == "budget_constraint")
    assert budget_criterion.passed is False
