import pytest
from app.schemas.run import Run, RunStatus
from app.services.repository import InMemoryRunRepository
from app.services.reliability_service import ReliabilityService


def test_reliability_calculation_empty():
    repo = InMemoryRunRepository()
    service = ReliabilityService(repo=repo)
    metrics = service.calculate_reliability()
    assert metrics.total_runs == 0
    assert metrics.successful_runs == 0
    assert metrics.failed_runs == 0
    assert metrics.overall_reliability_percentage == 0.0


def test_reliability_calculation_from_real_runs():
    repo = InMemoryRunRepository()
    service = ReliabilityService(repo=repo)

    # 3 successful runs, 1 failed run
    for i in range(3):
        repo.create(
            Run(
                id=f"run-succ-{i}",
                task_id="task-1",
                scenario_mode="normal",
                agent_type="deterministic",
                agent_retry_policy="unsafe_retry",
                status=RunStatus.COMPLETED,
                created_at="2026-10-01T08:00:00Z",
            )
        )

    repo.create(
        Run(
            id="run-fail-1",
            task_id="task-1",
            scenario_mode="timeout_after_commit",
            agent_type="deterministic",
            agent_retry_policy="unsafe_retry",
            status=RunStatus.FAILED,
            created_at="2026-10-01T08:00:00Z",
        )
    )

    metrics = service.calculate_reliability()
    assert metrics.total_runs == 4
    assert metrics.successful_runs == 3
    assert metrics.failed_runs == 1
    assert metrics.overall_reliability_percentage == 75.0
    assert metrics.by_scenario["normal"] == 100.0
    assert metrics.by_scenario["timeout_after_commit"] == 0.0
