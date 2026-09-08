from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from app.schemas.task import Task
from app.schemas.run import Run


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


# Global instances
task_repository = InMemoryTaskRepository()
run_repository = InMemoryRunRepository()
