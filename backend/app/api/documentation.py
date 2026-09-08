from fastapi import APIRouter, HTTPException
from app.schemas.documentation import APIDocumentation
from app.services.integration_service import integration_service
from app.services.documentation_service import documentation_service

router = APIRouter(prefix="/documentation", tags=["API Documentation Builder"])


@router.get("/{integration_id}", response_model=APIDocumentation)
def get_or_generate_documentation(integration_id: str):
    """Generate structured, contract-derived API documentation for an integration."""
    integration = integration_service.get_integration(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail=f"Integration {integration_id} not found")
    return documentation_service.generate_documentation(integration)
