from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import BaseModel

class AddressModel(BaseModel):
    __tablename__ = 'addresses'

    id_key = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    street = Column(String(200))
    city = Column(String(100))
    state = Column(String(100))
    zip_code = Column(String(20))

    # Clave foránea: vincula cada dirección a un cliente
    client_id_key = Column(
        Integer,
        ForeignKey('clients.id_key', ondelete='CASCADE'),  # Si se elimina el cliente, se eliminan sus direcciones
        nullable=False,
        index=True
    )

    # Relación con ClientModel
    client = relationship("ClientModel", back_populates="addresses")

    def __repr__(self):
        return f"<Address(id_key={self.id_key}, city='{self.city}')>"
