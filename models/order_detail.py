from sqlalchemy import Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from models.base_model import BaseModel

class OrderDetailModel(BaseModel):
    __tablename__ = "order_details"

    id_key = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)

    quantity = Column(Integer)
    price = Column(Float)
    order_id = Column(Integer, ForeignKey("orders.id_key"), index=True)
    product_id = Column(Integer, ForeignKey("products.id_key"), index=True)

    # Relaciones
    order = relationship("OrderModel", back_populates="order_details", lazy="select")
    product = relationship("ProductModel", back_populates="order_details", lazy="select")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<OrderDetail(id_key={self.id_key}, product_id={self.product_id})>"
