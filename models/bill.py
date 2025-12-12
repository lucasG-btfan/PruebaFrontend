from sqlalchemy import Column, String, Float, Date, Enum, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base_model import BaseModel
from models.enums import PaymentType

class BillModel(BaseModel):
    __tablename__ = "bills"

    id_key = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)

    # Campos de factura
    bill_number = Column(String, unique=True, index=True, nullable=False)
    discount = Column(Float)
    date = Column(Date)
    total = Column(Float)
    payment_type = Column(Enum(PaymentType))

    # Claves foráneas
    client_id_key = Column(Integer, ForeignKey('clients.id_key'), index=True)
    order_id_key = Column(Integer, ForeignKey('orders.id_key'), index=True, nullable=True)

    # Relaciones
    order = relationship('OrderModel', back_populates='bill', uselist=False, lazy="select")
    client = relationship('ClientModel', back_populates='bills', lazy="select")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Bill(id_key={self.id_key}, bill_number='{self.bill_number}')>"
