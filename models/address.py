from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base_model import BaseModel

class AddressModel(BaseModel):
    __tablename__ = 'addresses'

    id_key = Column(Integer, primary_key=True, index=True)
    client_id_key = Column(Integer, ForeignKey('clients.id_key', ondelete='CASCADE'), nullable=False)
    address_type = Column(String(50), default='shipping')
    street = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100))
    zip_code = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación con Client
    client = relationship("ClientModel", back_populates="addresses")

    def __repr__(self):
        return f"<Address(id={self.id_key}, client={self.client_id_key}, {self.street[:30]}...)>"