from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base_model import BaseModel
from models.enums import DeliveryMethod, Status

class OrderModel(BaseModel):
    __tablename__ = "orders"

    id_key = Column(Integer, primary_key=True, index=True, nullable=False)

    # Campos de orden
    date = Column(DateTime, index=True, default=func.now())
    total = Column(Float, nullable=False)
    delivery_method = Column(Integer, nullable=False)
    status = Column(Integer, nullable=False)
    address = Column(String, nullable=True)

    # Claves foráneas
    client_id = Column(Integer, ForeignKey('clients.id_key'), index=True)
    bill_id = Column(Integer, ForeignKey('bills.id_key'), nullable=True)

    # Relación con BillModel (uno-a-uno bidireccional)
    bill = relationship(
        "BillModel",
        back_populates="order",
        foreign_keys="BillModel.order_id",
        uselist=False,
        lazy="select",
        remote_side="BillModel.order_id"
    )

    # Relación con cliente
    client = relationship(
        "ClientModel",
        back_populates="orders",
        lazy="select"
    )

    # Relación con detalles de orden (productos)
    order_details = relationship(
        "OrderDetailModel",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Order(id_key={self.id_key}, date={self.date})>"
