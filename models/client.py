# models/client.py
"""
Client model for storing client information.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base_model import BaseModel

class ClientModel(BaseModel):  # <-- Cambiado de ClientModel a Client
    """
    Client model representing users/customers.
    """
    __tablename__ = 'clients'

    # Basic information
    id_key = Column(Integer, primary_key=True, index=True)
    id = Column(Integer, unique=True, nullable=True)
    name = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    company = Column(String(100))
    tax_id = Column(String(50))
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    addresses = relationship("AddressModel", back_populates="client",
                           cascade="all, delete-orphan", lazy="select")
    orders = relationship("OrderModel", back_populates="client",
                         cascade="all, delete-orphan", lazy="select")
    bills = relationship("BillModel", back_populates="client",
                        cascade="all, delete-orphan", lazy="select")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Asegurar que id_key tenga valor
        if self.id_key is None and self.id is not None:
            self.id_key = self.id
        elif self.id is None and self.id_key is not None:
            self.id = self.id_key  # Para compatibilidad temporal

    def __repr__(self):
        return f"<Client(id_key={self.id_key}, email='{self.email}', name='{self.name}', lastname='{self.lastname}')>"