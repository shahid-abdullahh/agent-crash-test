from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.schemas.run import Run, RunCreateRequest
from app.schemas.trace import TraceEvent
from app.schemas.evaluation import EvaluationResult
from app.schemas.diagnosis import DiagnosisResult
from app.services.run_service import run_service

router = APIRouter(prefix="/runs", tags=["Runs"])


@router.get("", response_model=List[Run])
def list_runs():
    return run_service.list_runs()


@router.post("", response_model=Run)
async def create_and_execute_run(payload: RunCreateRequest):
    return await run_service.execute_run(payload)


@router.get("/{run_id}", response_model=Run)
def get_run(run_id: str):
    run = run_service.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return run


@router.get("/{run_id}/trace", response_model=List[TraceEvent])
def get_run_trace(run_id: str):
    run = run_service.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return run.trace


@router.get("/{run_id}/evaluation", response_model=EvaluationResult)
def get_run_evaluation(run_id: str):
    run = run_service.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    if not run.evaluation:
        raise HTTPException(status_code=404, detail=f"Evaluation for run {run_id} not found")
    return run.evaluation


@router.get("/{run_id}/diagnosis", response_model=Optional[DiagnosisResult])
def get_run_diagnosis(run_id: str):
    run = run_service.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return run.diagnosis
