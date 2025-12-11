from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import BaseModel

class AddressModel(BaseModel):
    __tablename__ = 'addresses'

    id_key = Column(Integer, primary_key=True, index=True)
    client_id_key = Column(Integer, ForeignKey("clients.id_key"), nullable=False, index=True)
    street = Column(String(200))
    city = Column(String(100))
    state = Column(String(100))
    zip_code = Column(String(20))

    # Relación
    client = relationship("ClientModel", back_populates="addresses")

    def __repr__(self):
        return f"<Address(id_key={self.id_key}, city='{self.city}')>"
