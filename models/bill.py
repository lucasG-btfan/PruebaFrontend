from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from models.base_model import BaseModel
from models.enums import PaymentType

class BillModel(BaseModel):
    __tablename__ = "bills"

    id_key = Column(Integer, primary_key=True, index=True, nullable=False)

    # Campos de factura
    bill_number = Column(String, unique=True, index=True, nullable=False)
    discount = Column(Float, default=0.0)
    date = Column(DateTime)
    total = Column(Float, nullable=False)
    payment_type = Column(Integer, nullable=False)
    subtotal = Column(Float, nullable=True)

    # Claves foráneas
    client_id_key = Column(Integer, ForeignKey('clients.id_key'), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id_key'), unique=True, nullable=False)

    # Relación con orden
    order = relationship(
        "OrderModel",
        back_populates="bill",
        foreign_keys=[order_id],
        uselist=False,
        lazy="select"
    )

    # Relación con cliente
    client = relationship(
        "ClientModel",
        back_populates="bills",
        lazy="select",
        foreign_keys=[client_id_key]
    )

    def __init__(self, **kwargs):

        if 'client_id' in kwargs and 'client_id_key' not in kwargs:
            kwargs['client_id_key'] = kwargs.pop('client_id')
        elif 'client_id_key' in kwargs and 'client_id' not in kwargs:
            kwargs['client_id'] = kwargs.pop('client_id_key')
        
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Bill(id_key={self.id_key}, bill_number='{self.bill_number}')>"
