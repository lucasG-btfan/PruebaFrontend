# models/bill.py
from sqlalchemy import Column, String, Float, Date, Enum, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base_model import BaseModel
from models.enums import PaymentType

class BillModel(BaseModel):
    __tablename__ = "bills"
    # Campos
    id_key = Column(Integer, primary_key=True, index=True)
    id = Column(Integer, unique=True, nullable=True)
    bill_number = Column(String, unique=True, index=True, nullable=False)
    discount = Column(Float)
    date = Column(Date)
    total = Column(Float)
    payment_type = Column(Enum(PaymentType))
    # Claves foráneas
    client_id_key = Column(Integer, ForeignKey('clients.id_key'), index=True)
    order_id_key = Column(Integer, ForeignKey('orders.id_key'), index=True, nullable=True)

    # Relación con OrderModel (especifica foreign_keys)
    order = relationship(
        'OrderModel',
        back_populates='bill',
        uselist=False,
        lazy="select",
        foreign_keys=[order_id_key]  # Especifica la clave foránea
    )

    client = relationship('ClientModel', back_populates='bills', lazy="select")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id_key is None and self.id is not None:
            self.id_key = self.id
        elif self.id is None and self.id_key is not None:
            self.id = self.id_key
