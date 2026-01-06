from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
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
import logging
from jose import jwt
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()

# Configuración JWT - DEBE SER IGUAL QUE auth_controller.py
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"

def get_current_user_id_key(authorization: str = Query(None, alias="authorization")):
    """
    DEPENDENCIA SIMPLIFICADA - Solo para diagnóstico
    """
    logger.info(f"🔍 [DEPENDENCY] Authorization: {authorization}")
    
    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("⚠️ [DEPENDENCY] No Bearer token found")
        return 0  # Default to admin for testing
    
    token = authorization[7:]  # Remove "Bearer "
    logger.info(f"🔍 [DEPENDENCY] Token: {token[:50]}...")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        client_id = payload.get("sub")
        
        if client_id is None:
            logger.error("❌ [DEPENDENCY] No 'sub' in payload")
            return 0
        
        # Convertir a int
        client_id_int = int(client_id)
        logger.info(f"✅ [DEPENDENCY] Client ID: {client_id_int}")
        return client_id_int
        
    except jwt.ExpiredSignatureError:
        logger.error("❌ [DEPENDENCY] Token expired")
        return 0
    except jwt.JWTError as e:
        logger.error(f"❌ [DEPENDENCY] JWT Error: {str(e)}")
        return 0
    except Exception as e:
        logger.error(f"❌ [DEPENDENCY] Unexpected error: {str(e)}")
        return 0

@router.get("/test", response_model=dict)
async def test_endpoint():
    """Test endpoint - NO requiere autenticación"""
    return {
        "message": "✅ Clientes endpoint funcionando",
        "status": "online",
        "timestamp": "2026-01-06T12:00:00Z"
    }

@router.get("/debug", response_model=dict)
async def debug_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    auth: Optional[str] = Query(None, alias="authorization"),
    db: Session = Depends(get_db)
):
    """Endpoint de debug - muestra TODO"""
    logger.info(f"🔍 [DEBUG] skip={skip}, limit={limit}, auth={auth}")
    
    # Contar clientes
    total_clients = db.query(ClientModel).filter(
        ClientModel.is_active == True
    ).count()
    
    # Obtener algunos clientes
    clients = db.query(ClientModel).filter(
        ClientModel.is_active == True
    ).offset(skip).limit(limit).all()
    
    return {
        "debug": True,
        "skip": skip,
        "limit": limit,
        "total_clients": total_clients,
        "clients_count": len(clients),
        "auth_header_present": auth is not None,
        "auth_header": auth[:50] + "..." if auth else None,
        "clients": [
            {
                "id": c.id_key,
                "name": c.name,
                "email": c.email
            }
            for c in clients
        ]
    }

@router.get("/simple", response_model=List[dict])
async def get_clients_simple(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Endpoint SIMPLE - sin autenticación para testing"""
    try:
        clients = db.query(ClientModel).filter(
            ClientModel.is_active == True
        ).offset(skip).limit(limit).all()
        
        return [
            {
                "id_key": c.id_key,
                "name": c.name,
                "lastname": c.lastname,
                "email": c.email,
                "phone": c.phone,
                "is_active": c.is_active
            }
            for c in clients
        ]
    except Exception as e:
        logger.error(f"❌ Error en simple endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=ClientListResponseSchema)
async def get_clients(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Máximo número de registros"),
    authorization: Optional[str] = Query(None),  # Cambiado a Query
    db: Session = Depends(get_db)
):
    """Obtener lista de clientes - VERSIÓN SIMPLIFICADA"""
    logger.info(f"🔍 [GET /clients] Iniciando - skip={skip}, limit={limit}")
    
    try:
        # Obtener user_id de la dependencia
        current_user_id_key = get_current_user_id_key(authorization)
        logger.info(f"🔍 [GET /clients] User ID: {current_user_id_key}")
        
        # Query base
        query = db.query(ClientModel).filter(
            ClientModel.is_active == True
        )
        
        # Filtrar si no es admin
        if current_user_id_key != 0:
            query = query.filter(ClientModel.id_key == current_user_id_key)
            logger.info(f"🔍 [GET /clients] Filtrando para cliente {current_user_id_key}")
        else:
            logger.info("🔍 [GET /clients] Admin - mostrando todos")
        
        # Contar total
        total = query.count()
        logger.info(f"🔍 [GET /clients] Total clientes: {total}")
        
        # Obtener resultados paginados
        clients = query.offset(skip).limit(limit).all()
        logger.info(f"🔍 [GET /clients] Clientes obtenidos: {len(clients)}")
        
        # Calcular paginación
        pages = max(1, (total + limit - 1) // limit) if limit > 0 else 1
        current_page = max(1, (skip // limit) + 1) if limit > 0 else 1
        
        logger.info(f"✅ [GET /clients] Enviando respuesta - page={current_page}, pages={pages}")
        
        return {
            "items": clients,
            "total": total,
            "page": current_page,
            "size": limit,
            "pages": pages
        }
        
    except Exception as e:
        logger.error(f"❌ [GET /clients] ERROR: {str(e)}", exc_info=True)
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error: {str(e)}"
        )

# Mantén las otras funciones (get, post, put, delete) iguales
@router.get("/{client_id}", response_model=ClientResponseSchema)
async def get_client(
    client_id: int,
    authorization: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get client by ID - versión simplificada"""
    logger.info(f"🔍 [GET /clients/{client_id}]")
    
    current_user_id_key = get_current_user_id_key(authorization)
    
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
            detail=f"Client {client_id} not found"
        )
    
    return client