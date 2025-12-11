# models/order.py
from sqlalchemy import Column, Float, DateTime, Enum, Integer, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import BaseModel
from models.enums import DeliveryMethod, Status

class OrderModel(BaseModel):
    __tablename__ = "orders"
    id_key = Column(Integer, primary_key=True, index=True)
    id = Column(Integer, unique=True, nullable=True)
    date = Column(DateTime, index=True)
    total = Column(Float)
    delivery_method = Column(Enum(DeliveryMethod), index=True)
    status = Column(Enum(Status), index=True)
    client_id_key = Column(Integer, ForeignKey('clients.id_key'), index=True)

    # Elimina esta línea para evitar el conflicto:
    # bill_id = Column(Integer, ForeignKey('bills.id'), index=True)

    order_details = relationship(
        "OrderDetailModel",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="select"
    )
    client = relationship("ClientModel", back_populates="orders", lazy="select")

    # Relación con BillModel (especifica foreign_keys)
    bill = relationship(
        "BillModel",
        back_populates="order",
        lazy="select",
        foreign_keys="[BillModel.order_id_key]"  # Usa la clave foránea de BillModel
    )
