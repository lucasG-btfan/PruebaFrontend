from sqlalchemy import Column, String, Float, Text, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from models.base_model import BaseModel

class ProductModel(BaseModel):
    __tablename__ = "products"

    id_key = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    price = Column(Float, nullable=False, index=True)
    stock = Column(Integer, default=0, nullable=False, index=True)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey('categories.id_key'), index=True)

    # Relaciones
    category = relationship('CategoryModel', back_populates='products', lazy='select')
    reviews = relationship('ReviewModel', back_populates='product', cascade='all, delete-orphan', lazy='select')
    order_details = relationship('OrderDetailModel', back_populates='product', cascade='all, delete-orphan', lazy='select')

    def __repr__(self):
        return f"<Product(id_key={self.id_key}, name='{self.name}')>"
