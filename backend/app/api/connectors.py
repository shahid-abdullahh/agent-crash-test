from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.connector import ConnectorDefinition
from app.services.integration_service import integration_service

router = APIRouter(prefix="/connectors", tags=["Connectors"])


@router.get("", response_model=List[ConnectorDefinition])
def list_connectors():
    """List all registered system connectors."""
    return integration_service.list_connectors()


@router.get("/{connector_id}", response_model=ConnectorDefinition)
def get_connector(connector_id: str):
    """Get connector details by ID."""
    conn = integration_service.get_connector(connector_id)
    if not conn:
        raise HTTPException(status_code=404, detail=f"Connector {connector_id} not found")
    return conn
