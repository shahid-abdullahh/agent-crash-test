import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base
from app.schemas.task import Task, TaskConstraints
from app.schemas.run import Run, RunStatus
from app.schemas.trace import TraceEvent, TraceEventType, HTTPPayload
from app.schemas.evaluation import EvaluationResult, CriterionResult, SideEffectEvaluation
from app.schemas.diagnosis import DiagnosisResult
from app.services.repository import SQLTaskRepository, SQLRunRepository
import app.db.session as session_module


def test_sql_repositories_crud():
    # Setup test in-memory SQLite engine
    test_engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=test_engine)
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    # Patch session_module
    session_module.engine = test_engine
    session_module.SessionLocal = TestSessionLocal

    task_repo = SQLTaskRepository()
    run_repo = SQLRunRepository()

    # 1. Test Task Persistence
    task = Task(
        id="sql-task-1",
        name="SQL Test Task",
        description="Book flight test",
        constraints=TaskConstraints(origin="DEL", destination="BOM", max_price=8000),
        expected_outcome_description="1 booking",
    )
    task_repo.create(task)
    loaded_task = task_repo.get("sql-task-1")
    assert loaded_task is not None
    assert loaded_task.name == "SQL Test Task"
    assert loaded_task.constraints.origin == "DEL"

    # 2. Test Run Persistence with Trace, Evaluation, and Diagnosis
    trace_events = [
        TraceEvent(
            event_id="sql-ev-1",
            run_id="sql-run-1",
            sequence_number=1,
            timestamp="2026-10-01T08:00:00Z",
            event_type=TraceEventType.HTTP_REQUEST,
            http_payload=HTTPPayload(method="POST", url="http://127.0.0.1:8000/sandbox/reservations"),
        ),
        TraceEvent(
            event_id="sql-ev-2",
            run_id="sql-run-1",
            sequence_number=2,
            timestamp="2026-10-01T08:00:01Z",
            event_type=TraceEventType.HTTP_RESPONSE,
            http_payload=HTTPPayload(method="POST", url="http://127.0.0.1:8000/sandbox/reservations", status_code=200, duration_ms=14.2),
        ),
    ]

    evaluation = EvaluationResult(
        run_id="sql-run-1",
        task_id="sql-task-1",
        success=True,
        criteria=[CriterionResult(name="budget", passed=True, expected=8000, actual=6500, message="Under budget")],
        side_effects=SideEffectEvaluation(is_safe=True, total_reservations_created=1, expected_reservations=1, duplicate_reservations_detected=0),
        reasons=["All passed"],
        evaluated_at="2026-10-01T08:00:02Z",
    )

    run = Run(
        id="sql-run-1",
        task_id="sql-task-1",
        scenario_mode="normal",
        agent_type="deterministic",
        agent_retry_policy="unsafe_retry",
        status=RunStatus.COMPLETED,
        trace=trace_events,
        evaluation=evaluation,
        created_at="2026-10-01T08:00:00Z",
    )

    run_repo.create(run)
    run_repo.update(run)

    loaded_run = run_repo.get("sql-run-1")
    assert loaded_run is not None
    assert loaded_run.status == RunStatus.COMPLETED
    assert len(loaded_run.trace) == 2
    assert loaded_run.trace[0].sequence_number == 1
    assert loaded_run.evaluation is not None
    assert loaded_run.evaluation.success is True
    assert loaded_run.evaluation.side_effects.is_safe is True
