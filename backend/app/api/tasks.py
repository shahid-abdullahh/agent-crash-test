from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.task import Task
from app.services.task_service import task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=List[Task])
def list_tasks():
    return task_service.list_tasks()


@router.post("", response_model=Task)
def create_task(task: Task):
    return task_service.create_task(task)


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: str):
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task
