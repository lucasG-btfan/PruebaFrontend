from __future__ import annotations  
from sqlalchemy import Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from models.base_model import BaseModel
from typing import TYPE_CHECKING

class OrderDetailModel(BaseModel):
    __tablename__ = "order_details"

    id_key = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    quantity = Column(Integer)
    price = Column(Float)
    order_id = Column(Integer, ForeignKey("orders.id_key"), index=True)
    product_id = Column(Integer, ForeignKey("products.id_key"), index=True)

    order = relationship("OrderModel", back_populates="details", lazy="select")
    product = relationship("ProductModel", back_populates="order_details", lazy="select")

    def __init__(self, **kwargs):
        name_mapping = {
            'order_id_key': 'order_id',
            'product_id_key': 'product_id'
        }

        new_kwargs = {}
        for key, value in kwargs.items():
            if key in name_mapping:
                new_key = name_mapping[key]
                new_kwargs[new_key] = value
            else:
                new_kwargs[key] = value

        super().__init__(**new_kwargs)

    def __repr__(self):
        return f"<OrderDetail(id_key={self.id_key}, product_id={self.product_id}, quantity={self.quantity})>"
