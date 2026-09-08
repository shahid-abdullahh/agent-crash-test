from typing import List, Optional
from app.schemas.trace import TraceEvent, TraceEventType
from app.schemas.evaluation import EvaluationResult
from app.schemas.diagnosis import DiagnosisResult
from app.sandbox.models import SandboxStateSnapshot


class FailureDiagnosisEngine:
    def diagnose(
        self,
        evaluation: EvaluationResult,
        trace_events: List[TraceEvent],
        sandbox_snapshot: SandboxStateSnapshot,
    ) -> Optional[DiagnosisResult]:
        if evaluation.success:
            return None

        # Analyze HTTP trace events for ambiguous timeout and retries
        http_requests = [e for e in trace_events if e.event_type == TraceEventType.HTTP_REQUEST]
        http_responses = [e for e in trace_events if e.event_type == TraceEventType.HTTP_RESPONSE]

        # Check for multiple POST /reservations
        post_res_events = [
            e for e in http_requests
            if e.http_payload and e.http_payload.method == "POST" and "/reservations" in e.http_payload.url
        ]

        # Check for 504 or error responses on POST /reservations
        timeout_res_events = [
            e for e in http_responses
            if e.http_payload and e.http_payload.status_code in (504, 502, 503)
        ]

        evidence_ids = []
        if post_res_events:
            evidence_ids.extend([e.event_id for e in post_res_events])
        if timeout_res_events:
            evidence_ids.extend([e.event_id for e in timeout_res_events])

        # Detect ambiguous timeout + unsafe retry + duplicate side effect
        if len(post_res_events) > 1 and len(timeout_res_events) > 0 and sandbox_snapshot.total_reservations > 1:
            return DiagnosisResult(
                failure_category="Ambiguous Operation Outcome & Unsafe Blind Retry",
                observed_behavior="State-changing POST /reservations request received a 504 Gateway Timeout after server committed reservation.",
                agent_behavior="Agent interpreted 504 status as total failure and issued an uncoordinated retry without Idempotency-Key or status query.",
                impact=f"Caused {sandbox_snapshot.total_reservations} reservations to be committed (duplicate side effect).",
                likely_responsibility="Agent / API Integration Protocol",
                recommended_remediation=(
                    "1. Introduce 'Idempotency-Key' header on all mutating POST requests.\n"
                    "2. Add fallback operation status verification (e.g. GET /reservations) before retrying mutating calls."
                ),
                evidence_events=evidence_ids,
            )

        # Fallback generic failure diagnosis
        return DiagnosisResult(
            failure_category="Task Constraint Violation or Execution Error",
            observed_behavior="Agent run did not meet all success criteria.",
            agent_behavior="Agent executed commands that resulted in constraint violations or missed target state.",
            impact=f"Evaluation failed with reasons: {'; '.join(evaluation.reasons)}",
            likely_responsibility="Agent Logic / Task Specification",
            recommended_remediation="Review task constraints and verify agent tool selection logic.",
            evidence_events=evidence_ids,
        )
