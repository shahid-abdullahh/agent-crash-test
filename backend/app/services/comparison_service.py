from typing import Optional, List
from fastapi import HTTPException
from app.schemas.comparison import RunComparison, RunComparisonSummary
from app.schemas.run import Run, RunStatus
from app.services.repository import run_repository, RunRepository


class ComparisonService:
    def __init__(self, repo: RunRepository = run_repository):
        self.repo = repo

    def compare_runs(self, baseline_run_id: str, remediated_run_id: str) -> RunComparison:
        baseline = self.repo.get(baseline_run_id)
        if not baseline:
            raise HTTPException(status_code=404, detail=f"Baseline run {baseline_run_id} not found")

        remediated = self.repo.get(remediated_run_id)
        if not remediated:
            raise HTTPException(status_code=404, detail=f"Remediated run {remediated_run_id} not found")

        def summarize_run(r: Run) -> RunComparisonSummary:
            total_res = 0
            dup_res = 0
            is_safe = False
            failure_cat = None

            if r.evaluation:
                total_res = r.evaluation.side_effects.total_reservations_created
                dup_res = r.evaluation.side_effects.duplicate_reservations_detected
                is_safe = r.evaluation.side_effects.is_safe

            if r.diagnosis:
                failure_cat = r.diagnosis.failure_category

            return RunComparisonSummary(
                run_id=r.id,
                scenario_mode=r.scenario_mode,
                agent_type=r.agent_type,
                agent_retry_policy=r.agent_retry_policy,
                status=r.status.value,
                total_reservations=total_res,
                duplicate_reservations=dup_res,
                is_safe=is_safe,
                trace_events_count=len(r.trace),
                failure_category=failure_cat,
            )

        b_summary = summarize_run(baseline)
        r_summary = summarize_run(remediated)

        status_transition = f"{b_summary.status.upper()} -> {r_summary.status.upper()}"
        side_effect_delta = (
            f"{b_summary.total_reservations} reservations ({b_summary.duplicate_reservations} duplicates) -> "
            f"{r_summary.total_reservations} reservation(s) ({r_summary.duplicate_reservations} duplicates)"
        )
        trace_delta = r_summary.trace_events_count - b_summary.trace_events_count

        remediation_effective = (
            b_summary.status == RunStatus.FAILED.value and r_summary.status == RunStatus.COMPLETED.value
        )

        findings: List[str] = []
        if b_summary.duplicate_reservations > 0 and r_summary.duplicate_reservations == 0:
            findings.append("Eliminated duplicate state mutations in the API sandbox.")
        if b_summary.status == RunStatus.FAILED.value and r_summary.status == RunStatus.COMPLETED.value:
            findings.append("Transformed uncoordinated agent failure into verifiable task success.")
        if r_summary.is_safe and not b_summary.is_safe:
            findings.append("Restored strict At-Most-Once side-effect safety invariants.")

        return RunComparison(
            baseline_run=b_summary,
            remediated_run=r_summary,
            status_transition=status_transition,
            side_effect_delta=side_effect_delta,
            trace_event_delta=trace_delta,
            remediation_strategy=f"Remediation policy: {remediated.agent_retry_policy}",
            remediation_effective=remediation_effective,
            key_findings=findings if findings else ["Both runs executed with nominal side-effects."],
        )


comparison_service = ComparisonService()
