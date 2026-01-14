from __future__ import annotations  
from sqlalchemy import Column, String, Float, Text, Integer, ForeignKey, CheckConstraint, DateTime, func
from sqlalchemy.orm import relationship
from models.base_model import BaseModel

class ProductModel(BaseModel):
    __tablename__ = "products"

    id_key = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    price = Column(Float, nullable=False, index=True)
    stock = Column(Integer, default=0, nullable=False, index=True)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("categories.id_key"), nullable=True)
    sku = Column(String(100))
    image_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones usando strings para evitar importaciones circulares
    category = relationship('CategoryModel', back_populates='products', lazy='select')
    reviews = relationship('ReviewModel', back_populates='product', cascade='all, delete-orphan', lazy='select')
    order_details = relationship('OrderDetailModel', back_populates='product', cascade='all, delete-orphan', lazy='select')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Product(id_key={self.id_key}, name='{self.name}')>"
