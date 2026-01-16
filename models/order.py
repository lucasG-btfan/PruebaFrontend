# models/order.py
from __future__ import annotations
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base_model import BaseModel
from sqlalchemy import Enum as SQLAlchemyEnum
from models.enums import DeliveryMethod, Status
from typing import TYPE_CHECKING, Optional, Dict, Any

class OrderModel(BaseModel):
    __tablename__ = "orders"

    id_key = Column(Integer, primary_key=True, index=True, nullable=False)

    date = Column(DateTime, index=True, default=func.now())
    total = Column(Float, nullable=False)
    delivery_method = Column(SQLAlchemyEnum(DeliveryMethod), nullable=False)
    status = Column(SQLAlchemyEnum(Status), nullable=False)
    address = Column(String, nullable=True)
    delivered_date = Column(DateTime, nullable=True)

    # Claves foráneas
    client_id_key = Column(Integer, ForeignKey("clients.id_key"))
    bill_id = Column(Integer, ForeignKey("bills.id_key"), nullable=True)

    # Relación con BillModel (usando strings para evitar importaciones circulares)
    bill = relationship(
        "BillModel",
        back_populates="order",
        uselist=False,
        lazy="select",
        foreign_keys="[BillModel.order_id_key]",
        primaryjoin="BillModel.order_id_key == OrderModel.id_key"
    )

    # Relación con ClientModel (usando strings para evitar importaciones circulares)
    client = relationship("ClientModel", back_populates="orders", foreign_keys=[client_id_key])

    # Relación con OrderDetailModel (usando strings para evitar importaciones circulares)
    details = relationship(
        "OrderDetailModel",
        back_populates="order",
        lazy="select",
        cascade="all, delete-orphan",
        foreign_keys="[OrderDetailModel.order_id]"
    )

    def __init__(self, **kwargs):
        name_mapping: Dict[str, str] = {
            'client_id': 'client_id_key'
        }

        # Transformar nombres incorrectos a correctos
        new_kwargs: Dict[str, Any] = {}
        for key, value in kwargs.items():
            if key in name_mapping:
                new_key = name_mapping[key]
                print(f"Transformando {key} -> {new_key}")
                new_kwargs[new_key] = value
            else:
                new_kwargs[key] = value

        if 'order_number' in new_kwargs:
            del new_kwargs['order_number']

        super().__init__(**new_kwargs)

    def __repr__(self) -> str:
        return f"<Order(id_key={self.id_key}, date={self.date})>"