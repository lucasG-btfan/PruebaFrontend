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
    """Obtener direcciones de un cliente"""
    addresses = db.query(AddressModel).filter(
        AddressModel.client_id_key == client_id,
        AddressModel.is_active == True
    ).all()
    return addresses

@router.post("/", response_model=AddressSchema, status_code=status.HTTP_201_CREATED)
async def create_address(address_data: AddressCreateSchema, db: Session = Depends(get_db)):
    """Crear una nueva dirección"""
    # Verificar que el cliente exista
    client = db.query(ClientModel).filter(
        ClientModel.id_key == address_data.client_id_key,
        ClientModel.is_active == True
    ).first()
    
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Si es la primera dirección, marcar como default
    existing_addresses = db.query(AddressModel).filter(
        AddressModel.client_id_key == address_data.client_id_key
    ).count()
    
    if existing_addresses == 0:
        address_data.is_default = True
    
    # Si se marca como default, quitar default de otras direcciones
    if address_data.is_default:
        db.query(AddressModel).filter(
            AddressModel.client_id_key == address_data.client_id_key,
            AddressModel.is_default == True
        ).update({"is_default": False})
    
    address = AddressModel(**address_data.dict())
    db.add(address)
    db.commit()
    db.refresh(address)
    return address

@router.put("/{address_id}", response_model=AddressSchema)
async def update_address(address_id: int, address_data: AddressUpdateSchema, db: Session = Depends(get_db)):
    """Actualizar una dirección"""
    address = db.query(AddressModel).filter(
        AddressModel.id_key == address_id,
        AddressModel.is_active == True
    ).first()
    
    if not address:
        raise HTTPException(status_code=404, detail="Dirección no encontrada")
    
    update_data = address_data.dict(exclude_unset=True)
    
    # Si se marca como default, quitar default de otras direcciones
    if update_data.get('is_default') == True:
        db.query(AddressModel).filter(
            AddressModel.client_id_key == address.client_id_key,
            AddressModel.id_key != address_id,
            AddressModel.is_default == True
        ).update({"is_default": False})
    
    for key, value in update_data.items():
        setattr(address, key, value)
    
    db.commit()
    db.refresh(address)
    return address

@router.delete("/{address_id}", response_model=dict)
async def delete_address(address_id: int, db: Session = Depends(get_db)):
    """Eliminar una dirección (soft delete)"""
    address = db.query(AddressModel).filter(
        AddressModel.id_key == address_id,
        AddressModel.is_active == True
    ).first()
    
    if not address:
        raise HTTPException(status_code=404, detail="Dirección no encontrada")
    
    # Si es la dirección default, asignar otra como default
    if address.is_default:
        another_address = db.query(AddressModel).filter(
            AddressModel.client_id_key == address.client_id_key,
            AddressModel.id_key != address_id,
            AddressModel.is_active == True
        ).first()
        
        if another_address:
            another_address.is_default = True
    
    address.is_active = False
    db.commit()
    
    return {"message": "Dirección eliminada exitosamente"}