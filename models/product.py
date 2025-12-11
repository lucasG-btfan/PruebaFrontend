from sqlalchemy import Column, Integer, String, Float, Text, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import BaseModel

class ProductModel(BaseModel):
    """
    Class representing a product in the database.
    """
    __tablename__ = 'products'
    # Table-level constraints
    __table_args__ = (
        CheckConstraint('stock >= 0', name='check_product_stock_non_negative'),
    )

    id_key = Column(Integer, primary_key=True, index=True)
    id = Column(Integer, unique=True, nullable=True)  

    name = Column(String(255), nullable=False, index=True)
    price = Column(Float, nullable=False, index=True)
    stock = Column(Integer, default=0, nullable=False, index=True)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey('categories.id_key'), index=True)  

    # Relaciones
    category = relationship(
        'CategoryModel',
        back_populates='products',
        lazy='select',
    )
    reviews = relationship(
        'ReviewModel',
        back_populates='product',
        cascade='all, delete-orphan',
        lazy='select',
    )
    order_details = relationship(
        'OrderDetailModel',
        back_populates='product',
        cascade='all, delete-orphan',
        lazy='select',
    )
