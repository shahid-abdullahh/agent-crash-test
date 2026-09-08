import pytest
from app.diagnosis.engine import FailureDiagnosisEngine
from app.schemas.evaluation import EvaluationResult, CriterionResult, SideEffectEvaluation
from app.schemas.trace import TraceEvent, TraceEventType, HTTPPayload
from app.sandbox.models import SandboxStateSnapshot, ScenarioConfig, Reservation


def test_diagnosis_identifies_ambiguous_timeout():
    engine = FailureDiagnosisEngine()

    eval_res = EvaluationResult(
        run_id="run-diag-1",
        task_id="task-1",
        success=False,
        criteria=[
            CriterionResult(
                name="side_effect_safety",
                passed=False,
                expected={"reservations": 1},
                actual={"reservations": 2},
                message="Duplicate reservations detected",
            )
        ],
        side_effects=SideEffectEvaluation(
            is_safe=False,
            total_reservations_created=2,
            expected_reservations=1,
            duplicate_reservations_detected=1,
            unintended_state_mutations=["Duplicate reservation"],
        ),
        reasons=["Duplicate reservation"],
        evaluated_at="2026-10-01T08:00:00Z",
    )

    trace_events = [
        TraceEvent(
            event_id="ev-1",
            run_id="run-diag-1",
            sequence_number=1,
            timestamp="2026-10-01T08:00:01Z",
            event_type=TraceEventType.HTTP_REQUEST,
            http_payload=HTTPPayload(method="POST", url="http://testserver/sandbox/reservations"),
        ),
        TraceEvent(
            event_id="ev-2",
            run_id="run-diag-1",
            sequence_number=2,
            timestamp="2026-10-01T08:00:02Z",
            event_type=TraceEventType.HTTP_RESPONSE,
            http_payload=HTTPPayload(method="POST", url="http://testserver/sandbox/reservations", status_code=504),
        ),
        TraceEvent(
            event_id="ev-3",
            run_id="run-diag-1",
            sequence_number=3,
            timestamp="2026-10-01T08:00:03Z",
            event_type=TraceEventType.HTTP_REQUEST,
            http_payload=HTTPPayload(method="POST", url="http://testserver/sandbox/reservations"),
        ),
        TraceEvent(
            event_id="ev-4",
            run_id="run-diag-1",
            sequence_number=4,
            timestamp="2026-10-01T08:00:04Z",
            event_type=TraceEventType.HTTP_RESPONSE,
            http_payload=HTTPPayload(method="POST", url="http://testserver/sandbox/reservations", status_code=200),
        ),
    ]

    snapshot = SandboxStateSnapshot(
        scenario=ScenarioConfig(),
        total_reservations=2,
        reservations=[],
        flight_seats={},
    )

    diag = engine.diagnose(eval_res, trace_events, snapshot)
    assert diag is not None
    assert "Ambiguous Operation Outcome" in diag.failure_category
    assert "ev-1" in diag.evidence_events
    assert "ev-2" in diag.evidence_events
    assert "Idempotency-Key" in diag.recommended_remediation
