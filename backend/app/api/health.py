from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(tags=["System"])


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Agent Crash Test API",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
