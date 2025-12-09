# controllers/client_controller.py
"""
Client controller for handling client-related endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from config.database_render import get_db
from schemas.client_schema import (
    ClientCreateSchema,
    ClientUpdateSchema,
    ClientResponseSchema,
    ClientListResponseSchema
)
from services.client_service import ClientService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Redirigir /clients a /clients/ para consistencia
@router.get("", include_in_schema=False)
async def redirect_clients():
    """Redirect /clients to /clients/"""
    return RedirectResponse(url="/api/v1/clients/", status_code=307)

@router.post("", include_in_schema=False)
async def redirect_create_client():
    """Redirect POST /clients to POST /clients/"""
    return RedirectResponse(url="/api/v1/clients/", status_code=307)

# Rutas principales (con barra)
@router.get("/", response_model=ClientListResponseSchema)
async def get_clients(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """Get a list of clients with pagination."""
    service = ClientService(db)
    clients, total = service.get_all(skip=skip, limit=limit, is_active=is_active)

    return ClientListResponseSchema(
        items=clients,
        total=total,
        page=(skip // limit) + 1 if limit > 0 else 1,
        size=limit,
        pages=(total + limit - 1) // limit if limit > 0 else 1
    )

@router.get("/{client_id}", response_model=ClientResponseSchema)
async def get_client(client_id: int, db: Session = Depends(get_db)):
    """Get a specific client by ID."""
    service = ClientService(db)
    client = service.get_by_id(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )
    return client

@router.post("/", response_model=ClientResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_client(client_data: ClientCreateSchema, db: Session = Depends(get_db)):
    """Create a new client."""
    try:
        logger.info(f"Creating client: {client_data.email}")
        service = ClientService(db)
        result = service.create(client_data)
        logger.info(f"Client created: {result.id}")
        return result
    except Exception as e:
        logger.error(f"Error creating client: {str(e)}", exc_info=True)
        raise

@router.put("/{client_id}", response_model=ClientResponseSchema)
async def update_client(
    client_id: int,
    client_data: ClientUpdateSchema,
    db: Session = Depends(get_db)
):
    """Update an existing client."""
    service = ClientService(db)
    updated_client = service.update(client_id, client_data)
    if not updated_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )
    return updated_client

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(client_id: int, db: Session = Depends(get_db)):
    """Delete a client (soft delete)."""
    service = ClientService(db)
    success = service.delete(client_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )
