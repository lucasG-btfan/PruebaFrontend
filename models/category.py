from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from models.base_model import BaseModel

class CategoryModel(BaseModel):
    __tablename__ = "categories"

    id_key = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)

    # Relación con productos
    products = relationship("ProductModel", back_populates="category", lazy="select")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Category(id_key={self.id_key}, name='{self.name}')>"
