from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from schemas.address_schema import AddressCreateSchema, AddressUpdateSchema, AddressSchema
from models.address import AddressModel
from models.client import ClientModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/addresses", tags=["Addresses"])

@router.get("/client/{client_id}", response_model=List[AddressSchema])
async def get_client_addresses(client_id: int, db: Session = Depends(get_db)):
    """Obtener direcciones de un cliente (incluyendo admin si client_id=0)"""
    addresses = db.query(AddressModel).filter(
        AddressModel.client_id_key == client_id
    ).all()
    return addresses

@router.get("/store", response_model=AddressSchema)
async def get_store_address(db: Session = Depends(get_db)):
    """Obtener dirección del local (client_id_key = 0)"""
    address = db.query(AddressModel).filter(
        AddressModel.client_id_key == 0
    ).first()

    if not address:
        raise HTTPException(
            status_code=404,
            detail="Dirección del local no encontrada"
        )

    return address

@router.post("/", response_model=AddressSchema, status_code=status.HTTP_201_CREATED)
async def create_address(
    address_data: AddressCreateSchema,
    db: Session = Depends(get_db)
):
    """Crear una nueva dirección para un cliente (no permitir client_id_key=0)"""
    if address_data.client_id_key == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="client_id_key=0 está reservado para la dirección del local"
        )

    client = db.query(ClientModel).filter(
        ClientModel.id_key == address_data.client_id_key
    ).first()

    if not client:
        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado"
        )

    address = AddressModel(**address_data.dict())
    db.add(address)
    db.commit()
    db.refresh(address)

    logger.info(f"Dirección creada: ID {address.id_key} para cliente {address.client_id_key}")
    return address

@router.put("/{address_id}", response_model=AddressSchema)
async def update_address(
    address_id: int,
    address_data: AddressUpdateSchema,
    db: Session = Depends(get_db)
):
    """Actualizar una dirección de cliente (no permitir modificar dirección del local)"""
    address = db.query(AddressModel).filter(
        AddressModel.id_key == address_id
    ).first()

    if not address:
        raise HTTPException(
            status_code=404,
            detail="Dirección no encontrada"
        )

    if address.client_id_key == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La dirección del local solo puede modificarse desde /addresses/store"
        )

    update_data = address_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(address, key, value)

    db.commit()
    db.refresh(address)

    logger.info(f"Dirección actualizada: ID {address.id_key}")
    return address

@router.put("/store", response_model=AddressSchema)
async def update_store_address(
    address_data: AddressUpdateSchema,
    db: Session = Depends(get_db)
):
    """Actualizar dirección del local (client_id_key=0)"""
    address = db.query(AddressModel).filter(
        AddressModel.client_id_key == 0
    ).first()

    if not address:
        address_data_dict = address_data.dict(exclude_unset=True)
        address_data_dict.update({
            "client_id_key": 0,
            "street": address_data_dict.get("street", "Av. Principal #123"),
            "city": address_data_dict.get("city", "Buenos Aires"),
            "state": address_data_dict.get("state", "CABA"),
            "zip_code": address_data_dict.get("zip_code", "C1001")
        })
        address = AddressModel(**address_data_dict)
        db.add(address)
    else:
        update_data = address_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(address, key, value)

    db.commit()
    db.refresh(address)

    logger.info(f"Dirección del local actualizada")
    return address

@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar una dirección (no permitir eliminar dirección del local)"""
    address = db.query(AddressModel).filter(
        AddressModel.id_key == address_id
    ).first()

    if not address:
        raise HTTPException(
            status_code=404,
            detail="Dirección no encontrada"
        )

    if address.client_id_key == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se puede eliminar la dirección del local"
        )

    client_exists = db.query(ClientModel).filter(
        ClientModel.id_key == address.client_id_key
    ).first()

    if not client_exists:
        logger.warning(f"Cliente {address.client_id_key} no existe, eliminando dirección huérfana")

    db.delete(address)
    db.commit()

    logger.info(f"Dirección eliminada: ID {address_id}")
