from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from models.base_model import BaseModel

class CategoryModel(BaseModel):
    __tablename__ = "categories"

    id_key = Column(Integer, primary_key=True, index=True)
    id = Column(Integer, unique=True, nullable=True)  # Para migración o compatibilidad

    # Campos de categoría
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)

    # Relación con productos
    products = relationship("ProductModel", back_populates="category", lazy="select")
