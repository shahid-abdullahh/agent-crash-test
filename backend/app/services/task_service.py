import uuid
from typing import List, Optional
from app.schemas.task import Task, TaskConstraints
from app.services.repository import task_repository, TaskRepository


class TaskService:
    def __init__(self, repo: TaskRepository = task_repository):
        self.repo = repo
        self._init_default_tasks()

    def _init_default_tasks(self):
        if not self.repo.list():
            self.repo.create(
                Task(
                    id="task-book-cheapest-flight",
                    name="Book Cheapest Flight under ₹8,000",
                    description="Find and book the cheapest available flight from Delhi (DEL) to Mumbai (BOM) under ₹8,000 for passenger Rahul Sharma.",
                    constraints=TaskConstraints(
                        origin="DEL",
                        destination="BOM",
                        max_price=8000.0,
                        passenger_name="Rahul Sharma",
                        criteria_type="cheapest_under_budget",
                    ),
                    expected_outcome_description="A single confirmed reservation for flight FL-101 (price: 6500) under passenger Rahul Sharma.",
                )
            )

    def create_task(self, task: Task) -> Task:
        return self.repo.create(task)

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.repo.get(task_id)

    def list_tasks(self) -> List[Task]:
        return self.repo.list()


task_service = TaskService()
