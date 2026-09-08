from typing import Dict, List
from app.schemas.reliability import ReliabilityOverview, TaskReliabilityMetric
from app.schemas.run import RunStatus
from app.services.repository import run_repository, RunRepository


class ReliabilityService:
    def __init__(self, repo: RunRepository = run_repository):
        self.repo = repo

    def calculate_reliability(self) -> ReliabilityOverview:
        runs = self.repo.list()
        total_runs = len(runs)
        if total_runs == 0:
            return ReliabilityOverview(
                total_runs=0,
                successful_runs=0,
                failed_runs=0,
                overall_reliability_percentage=0.0,
                by_scenario={},
                by_task=[],
            )

        successful_runs = sum(1 for r in runs if r.status == RunStatus.COMPLETED)
        failed_runs = sum(1 for r in runs if r.status == RunStatus.FAILED)
        overall_pct = round((successful_runs / total_runs) * 100.0, 2)

        # By Scenario
        scenarios: Dict[str, List[bool]] = {}
        for r in runs:
            scenarios.setdefault(r.scenario_mode, []).append(r.status == RunStatus.COMPLETED)

        by_scenario = {
            scen: round((sum(1 for s in results if s) / len(results)) * 100.0, 2)
            for scen, results in scenarios.items()
        }

        # By Task
        tasks: Dict[str, List[bool]] = {}
        for r in runs:
            tasks.setdefault(r.task_id, []).append(r.status == RunStatus.COMPLETED)

        by_task = [
            TaskReliabilityMetric(
                task_id=task_id,
                total_runs=len(results),
                successful_runs=sum(1 for s in results if s),
                failed_runs=sum(1 for s in results if not s),
                reliability_percentage=round((sum(1 for s in results if s) / len(results)) * 100.0, 2),
            )
            for task_id, results in tasks.items()
        ]

        return ReliabilityOverview(
            total_runs=total_runs,
            successful_runs=successful_runs,
            failed_runs=failed_runs,
            overall_reliability_percentage=overall_pct,
            by_scenario=by_scenario,
            by_task=by_task,
        )


reliability_service = ReliabilityService()
