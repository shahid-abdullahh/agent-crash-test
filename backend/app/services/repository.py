import os
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from app.schemas.task import Task, TaskConstraints
from app.schemas.run import Run, RunStatus
from app.schemas.trace import TraceEvent, TraceEventType, HTTPPayload
from app.schemas.evaluation import EvaluationResult, CriterionResult, SideEffectEvaluation
from app.schemas.diagnosis import DiagnosisResult
from app.db.session import SessionLocal, init_db, DATABASE_URL, get_db_session
from app.db.models import SQLTask, SQLRun, SQLTraceEvent, SQLEvaluation, SQLDiagnosis


class TaskRepository(ABC):
    @abstractmethod
    def create(self, task: Task) -> Task:
        pass

    @abstractmethod
    def get(self, task_id: str) -> Optional[Task]:
        pass

    @abstractmethod
    def list(self) -> List[Task]:
        pass


class RunRepository(ABC):
    @abstractmethod
    def create(self, run: Run) -> Run:
        pass

    @abstractmethod
    def update(self, run: Run) -> Run:
        pass

    @abstractmethod
    def get(self, run_id: str) -> Optional[Run]:
        pass

    @abstractmethod
    def list(self) -> List[Run]:
        pass


class InMemoryTaskRepository(TaskRepository):
    def __init__(self):
        self._tasks: Dict[str, Task] = {}

    def create(self, task: Task) -> Task:
        self._tasks[task.id] = task
        return task

    def get(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def list(self) -> List[Task]:
        return list(self._tasks.values())


class InMemoryRunRepository(RunRepository):
    def __init__(self):
        self._runs: Dict[str, Run] = {}

    def create(self, run: Run) -> Run:
        self._runs[run.id] = run
        return run

    def update(self, run: Run) -> Run:
        self._runs[run.id] = run
        return run

    def get(self, run_id: str) -> Optional[Run]:
        return self._runs.get(run_id)

    def list(self) -> List[Run]:
        return list(self._runs.values())


class SQLTaskRepository(TaskRepository):
    def __init__(self):
        init_db()

    def create(self, task: Task) -> Task:
        session = get_db_session()
        if not session:
            return task
        with session:
            sql_task = SQLTask(
                id=task.id,
                name=task.name,
                description=task.description,
                constraints=task.constraints.model_dump(),
                expected_outcome_description=task.expected_outcome_description,
            )
            session.merge(sql_task)
            session.commit()
            return task

    def get(self, task_id: str) -> Optional[Task]:
        session = get_db_session()
        if not session:
            return None
        with session:
            sql_task = session.query(SQLTask).filter(SQLTask.id == task_id).first()
            if not sql_task:
                return None
            return Task(
                id=sql_task.id,
                name=sql_task.name,
                description=sql_task.description,
                constraints=TaskConstraints(**sql_task.constraints),
                expected_outcome_description=sql_task.expected_outcome_description,
            )

    def list(self) -> List[Task]:
        session = get_db_session()
        if not session:
            return []
        with session:
            tasks = session.query(SQLTask).all()
            return [
                Task(
                    id=t.id,
                    name=t.name,
                    description=t.description,
                    constraints=TaskConstraints(**t.constraints),
                    expected_outcome_description=t.expected_outcome_description,
                )
                for t in tasks
            ]


class SQLRunRepository(RunRepository):
    def __init__(self):
        init_db()

    def _convert_to_domain(self, sql_run: SQLRun) -> Run:
        trace_events: List[TraceEvent] = []
        for te in sql_run.trace_events:
            http_pl = HTTPPayload(**te.http_payload) if te.http_payload else None
            trace_events.append(
                TraceEvent(
                    event_id=te.event_id,
                    run_id=te.run_id,
                    sequence_number=te.sequence_number,
                    timestamp=te.timestamp,
                    event_type=TraceEventType(te.event_type),
                    tool_name=te.tool_name,
                    tool_arguments=te.tool_arguments,
                    http_payload=http_pl,
                    error_message=te.error_message,
                    metadata=te.metadata_payload,
                )
            )

        evaluation: Optional[EvaluationResult] = None
        if sql_run.evaluation:
            se = sql_run.evaluation
            evaluation = EvaluationResult(
                run_id=se.run_id,
                task_id=se.task_id,
                success=se.success,
                criteria=[CriterionResult(**c) for c in se.criteria],
                side_effects=SideEffectEvaluation(**se.side_effects),
                reasons=se.reasons,
                evaluated_at=se.evaluated_at,
            )

        diagnosis: Optional[DiagnosisResult] = None
        if sql_run.diagnosis:
            sd = sql_run.diagnosis
            diagnosis = DiagnosisResult(
                failure_category=sd.failure_category,
                observed_behavior=sd.observed_behavior,
                agent_behavior=sd.agent_behavior,
                impact=sd.impact,
                likely_responsibility=sd.likely_responsibility,
                recommended_remediation=sd.recommended_remediation,
                evidence_events=sd.evidence_events,
            )

        return Run(
            id=sql_run.id,
            task_id=sql_run.task_id,
            scenario_mode=sql_run.scenario_mode,
            agent_type=sql_run.agent_type,
            agent_retry_policy=sql_run.agent_retry_policy,
            status=RunStatus(sql_run.status),
            trace=trace_events,
            evaluation=evaluation,
            diagnosis=diagnosis,
            created_at=sql_run.created_at,
            completed_at=sql_run.completed_at,
            final_output=sql_run.final_output,
        )

    def create(self, run: Run) -> Run:
        session = get_db_session()
        if not session:
            return run
        with session:
            sql_run = SQLRun(
                id=run.id,
                task_id=run.task_id,
                scenario_mode=run.scenario_mode,
                agent_type=run.agent_type,
                agent_retry_policy=run.agent_retry_policy,
                status=run.status.value,
                created_at=run.created_at,
                completed_at=run.completed_at,
                final_output=run.final_output,
            )
            session.add(sql_run)
            session.commit()
            return run

    def update(self, run: Run) -> Run:
        session = get_db_session()
        if not session:
            return run
        with session:
            sql_run = session.query(SQLRun).filter(SQLRun.id == run.id).first()
            if not sql_run:
                return self.create(run)

            sql_run.status = run.status.value
            sql_run.completed_at = run.completed_at
            sql_run.final_output = run.final_output

            # Replace trace events
            session.query(SQLTraceEvent).filter(SQLTraceEvent.run_id == run.id).delete()
            for te in run.trace:
                session.add(
                    SQLTraceEvent(
                        event_id=te.event_id,
                        run_id=run.id,
                        sequence_number=te.sequence_number,
                        timestamp=te.timestamp,
                        event_type=te.event_type.value,
                        tool_name=te.tool_name,
                        tool_arguments=te.tool_arguments,
                        http_payload=te.http_payload.model_dump() if te.http_payload else None,
                        error_message=te.error_message,
                        metadata_payload=te.metadata,
                    )
                )

            # Update evaluation
            if run.evaluation:
                session.query(SQLEvaluation).filter(SQLEvaluation.run_id == run.id).delete()
                session.add(
                    SQLEvaluation(
                        run_id=run.id,
                        task_id=run.evaluation.task_id,
                        success=run.evaluation.success,
                        criteria=[c.model_dump() for c in run.evaluation.criteria],
                        side_effects=run.evaluation.side_effects.model_dump(),
                        reasons=run.evaluation.reasons,
                        evaluated_at=run.evaluation.evaluated_at,
                    )
                )

            # Update diagnosis
            if run.diagnosis:
                session.query(SQLDiagnosis).filter(SQLDiagnosis.run_id == run.id).delete()
                session.add(
                    SQLDiagnosis(
                        run_id=run.id,
                        failure_category=run.diagnosis.failure_category,
                        observed_behavior=run.diagnosis.observed_behavior,
                        agent_behavior=run.diagnosis.agent_behavior,
                        impact=run.diagnosis.impact,
                        likely_responsibility=run.diagnosis.likely_responsibility,
                        recommended_remediation=run.diagnosis.recommended_remediation,
                        evidence_events=run.diagnosis.evidence_events,
                    )
                )

            session.commit()
            return run

    def get(self, run_id: str) -> Optional[Run]:
        session = get_db_session()
        if not session:
            return None
        with session:
            sql_run = session.query(SQLRun).filter(SQLRun.id == run_id).first()
            if not sql_run:
                return None
            return self._convert_to_domain(sql_run)

    def list(self) -> List[Run]:
        session = get_db_session()
        if not session:
            return []
        with session:
            runs = session.query(SQLRun).all()
            return [self._convert_to_domain(r) for r in runs]


# Factory / Instance selection
if DATABASE_URL:
    task_repository: TaskRepository = SQLTaskRepository()
    run_repository: RunRepository = SQLRunRepository()
    PERSISTENCE_ENGINE = "SQL Database (" + DATABASE_URL.split("://")[0] + ")"
else:
    task_repository = InMemoryTaskRepository()
    run_repository = InMemoryRunRepository()
    PERSISTENCE_ENGINE = "InMemory"
