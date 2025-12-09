"""
Module for the AddressModel class.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from models.base_model import BaseModel


class AddressModel(BaseModel):
    """
    AddressModel class with attributes and relationships.
    """
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)  # ← 'id' no 'id_key'
    street = Column(String(200))
    city = Column(String(100))
    state = Column(String(100))
    zip_code = Column(String(20))
    
    # Relación
    client = relationship("ClientModel", back_populates="addresses")
