from fastapi import APIRouter
from app.sandbox.state import sandbox_state
from app.services.run_service import run_service
from app.services.task_service import task_service

router = APIRouter(prefix="/admin", tags=["Admin & Demo Controls"])


@router.post("/demo/reset")
def reset_demo_environment():
    """Reset sandbox state, demo runs, and restore default initial state."""
    sandbox_state.reset()
    # If run_repo is in-memory, we can reset run list
    if hasattr(run_service.run_repo, "_runs"):
        run_service.run_repo._runs.clear()

    return {
        "status": "reset",
        "message": "Demo environment successfully reset to default initial state.",
    }
