from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from config.database_render import get_db
from schemas.client_schema import (
    ClientCreateSchema,
    ClientUpdateSchema,
    ClientResponseSchema,
    ClientListResponseSchema
)
from models.client import ClientModel
from models.address import AddressModel
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
router = APIRouter()

# ⚠️ IMPORTANTE: La ruta /test debe estar ANTES de las rutas con parámetros
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

#Search para buscar un cliente
@router.get("/search", response_model=ClientListResponseSchema)
async def search_clients(
    q: str = Query(..., min_length=1, description="Término de búsqueda"),
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Máximo número de registros"),
    db: Session = Depends(get_db)
):
    """Buscar clientes por nombre, apellido o email."""
    try:
        logger.info(f"Searching clients: q={q}, skip={skip}, limit={limit}")
        
        # Crear filtro de búsqueda en múltiples campos
        search_filter = db.query(ClientModel).filter(
            ClientModel.is_active == True,
            func.lower(ClientModel.name).ilike(f"%{q.lower()}%") |
            func.lower(ClientModel.lastname).ilike(f"%{q.lower()}%") |
            func.lower(ClientModel.email).ilike(f"%{q.lower()}%") |
            func.lower(ClientModel.phone).ilike(f"%{q.lower()}%")
        )
        
        # Obtener resultados paginados
        clients = search_filter.offset(skip).limit(limit).all()
        
        # Contar total de resultados
        total = search_filter.count()
        
        # Calcular páginas
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

# GET todos los clientes con paginación
@router.get("", response_model=ClientListResponseSchema)
@router.get("/", response_model=ClientListResponseSchema)
async def get_clients(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Máximo número de registros"),
    db: Session = Depends(get_db)
):
    """Obtener lista de clientes con paginación."""
    try:
        logger.info(f"Fetching clients: skip={skip}, limit={limit}")
        
        # Obtener clientes activos
        clients = db.query(ClientModel).filter(
            ClientModel.is_active == True
        ).offset(skip).limit(limit).all()
        
        # Contar total de clientes activos
        total = db.query(ClientModel).filter(
            ClientModel.is_active == True
        ).count()
        
        # Calcular páginas
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

# POST crear cliente
@router.post("", response_model=ClientResponseSchema, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ClientResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_client(client_data: ClientCreateSchema, db: Session = Depends(get_db)):
    """Create a new client."""
    try:
        logger.info(f"Creating client: {client_data.email}")
        
        # Verificar si el email ya existe
        existing_client = db.query(ClientModel).filter(
            ClientModel.email == client_data.email
        ).first()

        if existing_client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Crear nuevo cliente - Asegúrate de que todos los campos requeridos estén presentes
        client_dict = client_data.dict(exclude={"address"})
        logger.info(f"Creating client with data: {client_dict}")
        
        client = ClientModel(**client_dict)
        db.add(client)
        db.commit()
        db.refresh(client)

        logger.info(f"Client created successfully: {client.id_key}")
        
        return client
        
    except HTTPException as he:
        # Re-lanzar las HTTPException
        logger.warning(f"HTTP Exception: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Error creating client: {str(e)}", exc_info=True)
        db.rollback()
        # Muestra el error completo
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Full traceback: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating client: {str(e)}"
        )

# GET cliente por ID
@router.get("/{client_id}", response_model=ClientResponseSchema)
async def get_client(client_id: int, db: Session = Depends(get_db)):
    """Get a specific client by id_key."""
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

@router.put("/{client_id}", response_model=ClientResponseSchema)
async def update_client(
    client_id: int,
    client_data: ClientUpdateSchema,
    db: Session = Depends(get_db)
):
    """Update an existing client."""
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
        # Actualizar solo los campos proporcionados
        update_data = client_data.dict(exclude_unset=True)
        
        # Excluir 'address' ya que no es un campo directo del modelo
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
async def delete_client(client_id: int, db: Session = Depends(get_db)):
    """Delete a client (soft delete)."""
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