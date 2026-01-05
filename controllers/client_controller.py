from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from config.database import get_db
from schemas.client_schema import (
    ClientCreateSchema,
    ClientUpdateSchema,
    ClientResponseSchema,
    ClientListResponseSchema
)
from models.client import ClientModel
from models.address import AddressModel
import logging
import math

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
router = APIRouter()

def get_current_user_id_key(authorization: str = Header(...)):
    try:
        return int(authorization.split(" ")[-1])
    except:
        return None

@router.get("/test")
async def test_clients():
    return {
        "message": "Endpoint de clientes funcionando",
        "example": {
            "id_key": 1,
            "name": "Juan",
            "lastname": "Pérez",
            "email": "juan@example.com"
        }
    }

@router.get("/search", response_model=ClientListResponseSchema)
async def search_clients(
    q: str = Query(..., min_length=1, description="Término de búsqueda"),
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Máximo número de registros"),
    db: Session = Depends(get_db),
    current_user_id_key: int = Depends(get_current_user_id_key)
):
    """Buscar clientes por nombre, apellido o email."""
    try:
        logger.info(f"Searching clients: q={q}, skip={skip}, limit={limit}")

        search_filter = db.query(ClientModel).filter(
            ClientModel.is_active == True,
            func.lower(ClientModel.name).ilike(f"%{q.lower()}%") |
            func.lower(ClientModel.lastname).ilike(f"%{q.lower()}%") |
            func.lower(ClientModel.email).ilike(f"%{q.lower()}%") |
            func.lower(ClientModel.phone).ilike(f"%{q.lower()}%")
        )

        if current_user_id_key != 0:
            search_filter = search_filter.filter(ClientModel.id_key == current_user_id_key)

        clients = search_filter.offset(skip).limit(limit).all()
        total = search_filter.count()
        pages = (total + limit - 1) // limit if limit > 0 else 1
        current_page = (skip // limit) + 1 if limit > 0 else 1

        logger.info(f"Search found {len(clients)} clients, total: {total}")
        return {
            "items": clients,
            "total": total,
            "page": current_page,
            "size": limit,
            "pages": pages
        }

    except Exception as e:
        logger.error(f"Error searching clients: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching clients: {str(e)}"
        )

@router.get("", response_model=ClientListResponseSchema)
@router.get("/", response_model=ClientListResponseSchema)
async def get_clients(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Máximo número de registros"),
    db: Session = Depends(get_db),
    current_user_id_key: int = Depends(get_current_user_id_key)
):
    """Obtener lista de clientes con paginación."""
    try:
        logger.info(f"Fetching clients: skip={skip}, limit={limit}")

        query = db.query(ClientModel).filter(
            ClientModel.is_active == True
        )

        if current_user_id_key != 0:
            query = query.filter(ClientModel.id_key == current_user_id_key)

        clients = query.offset(skip).limit(limit).all()
        total = query.count()

        pages = (total + limit - 1) // limit if limit > 0 else 1
        current_page = (skip // limit) + 1 if limit > 0 else 1

        logger.info(f"Found {len(clients)} clients, total: {total}, pages: {pages}")
        return {
            "items": clients,
            "total": total,
            "page": current_page,
            "size": limit,
            "pages": pages
        }
    except Exception as e:
        logger.error(f"Error fetching clients: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching clients: {str(e)}"
        )

@router.get("/{client_id}", response_model=ClientResponseSchema)
async def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user_id_key: int = Depends(get_current_user_id_key)
):
    """Get a specific client by id_key."""
    if current_user_id_key != 0 and client_id != current_user_id_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este perfil"
        )

    client = db.query(ClientModel).filter(
        ClientModel.id_key == client_id,
        ClientModel.is_active == True
    ).first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )
    return client

@router.post("", response_model=ClientResponseSchema, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ClientResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreateSchema,
    db: Session = Depends(get_db),
    current_user_id_key: int = Depends(get_current_user_id_key)
):
    """Create a new client."""
    # El admin no puede crear clientes
    if current_user_id_key == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin no puede crear clientes"
        )

    try:
        logger.info(f"Creating client: {client_data.email}")

        existing_client = db.query(ClientModel).filter(
            ClientModel.email == client_data.email
        ).first()

        if existing_client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        client_dict = client_data.dict(exclude={"address"})
        logger.info(f"Creating client with data: {client_dict}")

        client = ClientModel(**client_dict)
        db.add(client)
        db.commit()
        db.refresh(client)

        logger.info(f"Client created successfully: {client.id_key}")
        return client

    except HTTPException as he:
        logger.warning(f"HTTP Exception: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Error creating client: {str(e)}", exc_info=True)
        db.rollback()
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Full traceback: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating client: {str(e)}"
        )

@router.put("/{client_id}", response_model=ClientResponseSchema)
async def update_client(
    client_id: int,
    client_data: ClientUpdateSchema,
    db: Session = Depends(get_db),
    current_user_id_key: int = Depends(get_current_user_id_key)
):
    """Update an existing client."""
    # Si no es admin, solo puede actualizar su propio perfil
    if current_user_id_key != 0 and client_id != current_user_id_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este perfil"
        )

    client = db.query(ClientModel).filter(
        ClientModel.id_key == client_id,
        ClientModel.is_active == True
    ).first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )

    try:
        update_data = client_data.dict(exclude_unset=True)
        if 'address' in update_data:
            del update_data['address']

        for key, value in update_data.items():
            if hasattr(client, key):
                setattr(client, key, value)

        db.commit()
        db.refresh(client)
        return client

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating client: {str(e)}"
        )

@router.delete("/{client_id}", response_model=dict)
async def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user_id_key: int = Depends(get_current_user_id_key)
):
    """Delete a client (soft delete)."""
    # Si no es admin, solo puede eliminar su propio perfil
    if current_user_id_key != 0 and client_id != current_user_id_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar este perfil"
        )

    client = db.query(ClientModel).filter(
        ClientModel.id_key == client_id,
        ClientModel.is_active == True
    ).first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )

    try:
        client.is_active = False
        client.deleted_at = func.now()
        db.commit()
        return {"message": f"Client {client_id} deleted successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting client: {str(e)}"
        )
