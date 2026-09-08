from fastapi import APIRouter
from app.schemas.reliability import ReliabilityOverview
from app.services.reliability_service import reliability_service

router = APIRouter(prefix="/reliability", tags=["Reliability Engine"])


@router.get("", response_model=ReliabilityOverview)
def get_reliability_metrics():
    return reliability_service.calculate_reliability()
