# controllers/client_controller.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from config.database_render import get_db
from schemas.client_schema import (
    ClientCreateSchema,
    ClientUpdateSchema,
    ClientResponseSchema
)
from services.client_service import ClientService
from models.client import ClientModel
from models.address import AddressModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

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

        # Crear nuevo cliente (sin el campo 'address')
        client_dict = client_data.dict(exclude={"address"})
        client = ClientModel(**client_dict)
        db.add(client)
        db.commit()
        db.refresh(client)

        # Si se proporcionó una dirección, crear un registro en AddressModel
        if client_data.address:
            address = AddressModel(
                street=client_data.address,
                city="",  # Puedes establecer valores por defecto o dejar vacíos
                state="",
                zip_code="",
                client_id_key=client.id_key
            )
            db.add(address)
            db.commit()
            db.refresh(address)

        logger.info(f"Client created: {client.id_key}")
        return client
    except Exception as e:
        logger.error(f"Error creating client: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating client: {str(e)}"
        )
