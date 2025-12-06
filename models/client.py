# models/client.py - OPCIÓN ALTERNATIVA: Cambiar nombre a Client
"""
Client model for storing client information.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from models.base_model import BaseModel


class Client(BaseModel):  # <-- Cambiar de ClientModel a Client
    """
    Client model representing users/customers.
    """
    __tablename__ = 'clients'

    # Basic information
    full_name = Column(String(100), nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Optional fields for future use
    company = Column(String(100))
    tax_id = Column(String(50))
    notes = Column(String(500))
    
    # Soft delete support
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships (lazy loading to avoid import cycles)
    addresses = relationship("AddressModel", back_populates="client", 
                           cascade="all, delete-orphan", lazy="select")
    orders = relationship("OrderModel", back_populates="client", 
                         cascade="all, delete-orphan", lazy="select")
    bills = relationship("BillModel", back_populates="client", 
                        cascade="all, delete-orphan", lazy="select")

    def __repr__(self):
        return f"<Client(id={self.id}, email='{self.email}', full_name='{self.full_name}')>"