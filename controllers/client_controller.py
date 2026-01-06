from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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
from jose import jwt, JWTError
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
security = HTTPBearer()

def get_current_user_id_key(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """
    Extrae el client_id del token JWT.
    Esta función es una DEPENDENCIA de FastAPI.
    """
    try:
        token = credentials.credentials
        logger.info(f"🔐 Token recibido: {token[:50]}...")

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        client_id_str = payload.get("sub")

        if client_id_str is None:
            logger.error("❌ Token no contiene 'sub'")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing 'sub' field"
            )

        try:
            client_id = int(client_id_str)
            logger.info(f"✅ Client ID extraído: {client_id}")
            return client_id
        except ValueError:
            logger.error(f"❌ 'sub' no es un número válido: {client_id_str}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: 'sub' must be a number"
            )

    except jwt.ExpiredSignatureError:
        logger.error("❌ Token expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except JWTError as e:
        logger.error(f"❌ Error JWT: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        logger.error(f"❌ Error inesperado en autenticación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error"
        )

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

@router.get("/debug-auth")
async def debug_auth(current_user_id_key: int = Depends(get_current_user_id_key)):
    """Endpoint para debug de autenticación."""
    return {
        "current_user_id_key": current_user_id_key,
        "is_admin": current_user_id_key == 0,
        "message": "Auth debug funcionando correctamente"
    }

@router.get("/search", response_model=ClientListResponseSchema)
async def search_clients(
    q: str = Query(..., min_length=1, description="Término de búsqueda"),
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Máximo número de registros"),
    db: Session = Depends(get_db),
    current_user_id_key: int = Depends(get_current_user_id_key)
):
    """Buscar clientes por nombre, apellido, email o teléfono."""
    logger.info(f"🔍 [SEARCH] q={q}, skip={skip}, limit={limit}, user={current_user_id_key}")

    try:
        search_filter = db.query(ClientModel).filter(
            ClientModel.is_active == True,
            func.lower(ClientModel.name).ilike(f"%{q.lower()}%") |
            func.lower(ClientModel.lastname).ilike(f"%{q.lower()}%") |
            func.lower(ClientModel.email).ilike(f"%{q.lower()}%") |
            func.lower(ClientModel.phone).ilike(f"%{q.lower()}%")
        )

        # Filtrar por usuario si no es admin
        if current_user_id_key != 0:
            search_filter = search_filter.filter(ClientModel.id_key == current_user_id_key)

        # Obtener resultados
        clients = search_filter.offset(skip).limit(limit).all()
        total = search_filter.count()
        pages = (total + limit - 1) // limit if limit > 0 else 1
        current_page = (skip // limit) + 1 if limit > 0 else 1

        logger.info(f"✅ [SEARCH] Encontrados {len(clients)} clientes, total: {total}")
        
        return {
            "items": clients,
            "total": total,
            "page": current_page,
            "size": limit,
            "pages": pages
        }

    except Exception as e:
        logger.error(f"❌ Error searching clients: {str(e)}", exc_info=True)
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
    logger.info(f"🔍 [GET /clients] skip={skip}, limit={limit}, user={current_user_id_key}")

    try:
        # Construir query base
        query = db.query(ClientModel).filter(ClientModel.is_active == True)

        # Filtrar por usuario si no es admin
        if current_user_id_key != 0:
            query = query.filter(ClientModel.id_key == current_user_id_key)
            logger.info(f"🔍 Usuario regular: filtrando solo cliente {current_user_id_key}")
        else:
            logger.info(f"🔍 Admin: viendo todos los clientes")

        clients = query.offset(skip).limit(limit).all()
        total = query.count()

        pages = (total + limit - 1) // limit if limit > 0 else 1
        current_page = (skip // limit) + 1 if limit > 0 else 1

        logger.info(f"✅ [GET /clients] Retornando {len(clients)} clientes, total: {total}")

        return {
            "items": clients,
            "total": total,
            "page": current_page,
            "size": limit,
            "pages": pages
        }

    except Exception as e:
        logger.error(f"❌ Error fetching clients: {str(e)}", exc_info=True)
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
    """Obtener un cliente específico por id_key."""
    logger.info(f"🔍 [GET /clients/{client_id}] user={current_user_id_key}")

    # Verificar permisos
    if current_user_id_key != 0 and client_id != current_user_id_key:
        logger.warning(f"❌ Usuario {current_user_id_key} intentó acceder al perfil {client_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este perfil"
        )

    # Buscar cliente
    client = db.query(ClientModel).filter(
        ClientModel.id_key == client_id,
        ClientModel.is_active == True
    ).first()

    if not client:
        logger.warning(f"❌ Cliente {client_id} no encontrado")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )
    
    logger.info(f"✅ Cliente {client_id} encontrado")
    return client

@router.post("", response_model=ClientResponseSchema, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ClientResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreateSchema,
    db: Session = Depends(get_db),
    current_user_id_key: int = Depends(get_current_user_id_key)
):
    """Crear un nuevo cliente."""
    # El admin no puede crear clientes 
    if current_user_id_key == 0:
        logger.warning("❌ Admin intentó crear cliente desde /clients")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin no puede crear clientes. Use /auth/register"
        )

    try:
        logger.info(f"📝 Creando cliente: {client_data.email}")

        # Verificar email duplicado
        existing_client = db.query(ClientModel).filter(
            ClientModel.email == client_data.email
        ).first()

        if existing_client:
            logger.warning(f"❌ Email ya registrado: {client_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Crear cliente (sin address por ahora)
        client_dict = client_data.dict(exclude={"address"})
        client = ClientModel(**client_dict)
        
        db.add(client)
        db.commit()
        db.refresh(client)

        logger.info(f"✅ Cliente creado exitosamente: {client.id_key}")
        return client

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating client: {str(e)}", exc_info=True)
        db.rollback()
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
    """Actualizar un cliente existente."""
    logger.info(f"📝 [UPDATE] client_id={client_id}, user={current_user_id_key}")

    # Verificar permisos
    if current_user_id_key != 0 and client_id != current_user_id_key:
        logger.warning(f"❌ Usuario {current_user_id_key} intentó actualizar cliente {client_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este perfil"
        )

    # Buscar cliente
    client = db.query(ClientModel).filter(
        ClientModel.id_key == client_id,
        ClientModel.is_active == True
    ).first()

    if not client:
        logger.warning(f"❌ Cliente {client_id} no encontrado")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )

    try:
        # Actualizar solo campos enviados
        update_data = client_data.dict(exclude_unset=True)
        
        if 'address' in update_data:
            del update_data['address']

        # Aplicar cambios
        for key, value in update_data.items():
            if hasattr(client, key):
                setattr(client, key, value)

        db.commit()
        db.refresh(client)
        
        logger.info(f"✅ Cliente {client_id} actualizado exitosamente")
        return client

    except Exception as e:
        logger.error(f"❌ Error updating client: {str(e)}", exc_info=True)
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
    """Eliminar un cliente (soft delete)."""
    logger.info(f"🗑️ [DELETE] client_id={client_id}, user={current_user_id_key}")

    # Verificar permisos
    if current_user_id_key != 0 and client_id != current_user_id_key:
        logger.warning(f"❌ Usuario {current_user_id_key} intentó eliminar cliente {client_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar este perfil"
        )

    # Buscar cliente
    client = db.query(ClientModel).filter(
        ClientModel.id_key == client_id,
        ClientModel.is_active == True
    ).first()

    if not client:
        logger.warning(f"❌ Cliente {client_id} no encontrado")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )

    try:
        # Soft delete
        client.is_active = False
        client.deleted_at = func.now()
        
        db.commit()
        
        logger.info(f"✅ Cliente {client_id} eliminado exitosamente")
        return {"message": f"Client {client_id} deleted successfully"}

    except Exception as e:
        logger.error(f"❌ Error deleting client: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting client: {str(e)}"
        )