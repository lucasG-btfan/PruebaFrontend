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
    client_id_key = Column(Integer, ForeignKey("clients.id_key"))
    bill_id = Column(Integer, ForeignKey("bills.id_key"), nullable=True)

     # Relación con BillModel (uno-a-uno)
    bill = relationship(
        "BillModel",
        back_populates="order",
        uselist=False,
        lazy="select",
        foreign_keys="BillModel.order_id"  
    )

    # Relación con ClientModel
    client = relationship("ClientModel", back_populates="orders", foreign_keys=[client_id_key])
    details = relationship("OrderDetailModel", back_populates="order", lazy="select", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Order(id_key={self.id_key}, date={self.date})>"