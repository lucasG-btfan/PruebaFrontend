from sqlalchemy import Column, Float, DateTime, Enum, Integer, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import BaseModel
from models.enums import DeliveryMethod, Status

class OrderModel(BaseModel):
    __tablename__ = "orders"

    id_key = Column(Integer, primary_key=True, index=True)

    date = Column(DateTime, index=True)
    total = Column(Float)
    delivery_method = Column(Enum(DeliveryMethod), index=True)
    status = Column(Enum(Status), index=True)
    client_id_key = Column(Integer, ForeignKey('clients.id_key'), index=True)

    # Relaciones
    order_details = relationship("OrderDetailModel", back_populates="order", cascade="all, delete-orphan", lazy="select")
    client = relationship("ClientModel", back_populates="orders", lazy="select")
    bill = relationship("BillModel", back_populates="order", lazy="select")

    def __repr__(self):
        return f"<Order(id_key={self.id_key}, date={self.date})>"
