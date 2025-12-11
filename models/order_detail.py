from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import BaseModel

class OrderDetailModel(BaseModel):
    __tablename__ = "order_details"

    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id_key'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('products.id_key'), nullable=False, index=True)  

    # Relaciones
    order = relationship("OrderModel", back_populates="order_details", lazy="select")
    product = relationship("ProductModel", back_populates="order_details", lazy="select")
