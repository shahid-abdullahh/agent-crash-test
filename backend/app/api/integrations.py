from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.schemas.integration import Integration, IntegrationCreateRequest
from app.services.integration_service import integration_service

router = APIRouter(prefix="/integrations", tags=["API Integrations & Connectors"])


@router.get("", response_model=List[Integration])
def list_integrations():
    """List all registered API integrations."""
    return integration_service.list_integrations()


@router.post("", response_model=Integration)
async def create_integration(req: IntegrationCreateRequest):
    """Import and analyze an OpenAPI contract (URL or JSON/YAML content)."""
    return await integration_service.create_from_request(req)


@router.get("/{integration_id}", response_model=Integration)
def get_integration(integration_id: str):
    """Get detailed API integration information, operations, and AI-readiness findings."""
    integration = integration_service.get_integration(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail=f"Integration {integration_id} not found")
    return integration


@router.get("/{integration_id}/code")
def get_integration_code(integration_id: str) -> Dict[str, str]:
    """Generate and export integration client tools and connector code."""
    try:
        return integration_service.generate_client_code(integration_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
