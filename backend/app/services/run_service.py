import uuid
from datetime import datetime, timezone
from typing import List, Optional
import httpx
from fastapi import HTTPException

from app.schemas.run import Run, RunCreateRequest, RunStatus
from app.schemas.task import Task
from app.sandbox.state import sandbox_state
from app.sandbox.models import ScenarioConfig, ScenarioMode
from app.agent.tools import get_travel_tools, ToolExecutor
from app.agent.deterministic import DeterministicTravelAgent
from app.traces.collector import TraceCollector
from app.evaluator.deterministic import DeterministicEvaluator
from app.diagnosis.engine import FailureDiagnosisEngine
from app.services.repository import run_repository, RunRepository
from app.services.task_service import task_service, TaskService


class RunService:
    def __init__(
        self,
        run_repo: RunRepository = run_repository,
        t_service: TaskService = task_service,
        base_url: str = "http://127.0.0.1:8000",
    ):
        self.run_repo = run_repo
        self.task_service = t_service
        self.base_url = base_url
        self.evaluator = DeterministicEvaluator()
        self.diagnosis_engine = FailureDiagnosisEngine()

    async def execute_run(
        self,
        request: RunCreateRequest,
        custom_client: Optional[httpx.AsyncClient] = None,
        custom_agent: Optional[Any] = None,
    ) -> Run:
        task = self.task_service.get_task(request.task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {request.task_id} not found")

        run_id = f"run-{uuid.uuid4().hex[:8]}"
        created_at = datetime.now(timezone.utc).isoformat()

        run = Run(
            id=run_id,
            task_id=task.id,
            scenario_mode=request.scenario_mode,
            agent_type=request.agent_type,
            agent_retry_policy=request.agent_retry_policy,
            status=RunStatus.RUNNING,
            created_at=created_at,
        )
        self.run_repo.create(run)

        # 1. Reset sandbox & configure scenario mode
        sandbox_state.reset()
        scenario_enum = ScenarioMode.NORMAL
        try:
            scenario_enum = ScenarioMode(request.scenario_mode)
        except Exception:
            scenario_enum = ScenarioMode.NORMAL

        sandbox_state.configure_scenario(
            ScenarioConfig(
                mode=scenario_enum,
                fail_first_n_attempts=1,
            )
        )

        # 2. Setup trace collector and tool executor
        trace_collector = TraceCollector(run_id=run_id)
        tools = get_travel_tools()
        tool_executor = ToolExecutor(base_url=self.base_url, client=custom_client, tools=tools)

        # 3. Instantiate and run agent
        if custom_agent:
            agent = custom_agent
        elif request.agent_type == "llm":
            from app.agent.llm_agent import LLMAgent
            from app.agent.providers.openai_compatible import OpenAICompatibleProvider
            agent = LLMAgent(provider=OpenAICompatibleProvider())
        else:
            policy = (
                "violating_agent"
                if (
                    request.agent_type == "violating_agent"
                    or request.scenario_mode == "constraint_violation"
                    or request.agent_retry_policy == "violating_agent"
                )
                else request.agent_retry_policy
            )
            agent = DeterministicTravelAgent(retry_policy=policy)

        agent_output = await agent.run(
            task=task,
            tools=tools,
            tool_executor=tool_executor,
            trace_collector=trace_collector,
        )

        # 4. Evaluate execution against state & trace
        snapshot = sandbox_state.get_snapshot()
        trace_events = trace_collector.get_events()

        evaluation = self.evaluator.evaluate(
            run_id=run_id,
            task=task,
            trace_events=trace_events,
            sandbox_snapshot=snapshot,
            agent_output=agent_output,
        )

        # 5. Diagnose if failure occurred
        diagnosis = None
        if not evaluation.success:
            diagnosis = self.diagnosis_engine.diagnose(
                evaluation=evaluation,
                trace_events=trace_events,
                sandbox_snapshot=snapshot,
            )

        # 6. Update and persist run
        run.status = RunStatus.COMPLETED if evaluation.success else RunStatus.FAILED
        run.completed_at = datetime.now(timezone.utc).isoformat()
        run.trace = trace_events
        run.evaluation = evaluation
        run.diagnosis = diagnosis
        run.final_output = agent_output

        self.run_repo.update(run)
        return run

    def get_run(self, run_id: str) -> Optional[Run]:
        return self.run_repo.get(run_id)

    def list_runs(self) -> List[Run]:
        return self.run_repo.list()


run_service = RunService()
