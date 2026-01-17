"""Product repository for database operations."""
from sqlalchemy.orm import Session
from models.product import ProductModel
from repositories.base_repository_impl import BaseRepositoryImpl
from typing import Optional

class ProductRepository(BaseRepositoryImpl):
    """Repository for Product entity database operations."""

    def __init__(self, db: Session):
        from schemas.product_schema import ProductSchema
        super().__init__(ProductModel, ProductSchema, db)
    
    def exists(self, product_id: int) -> bool:
        """Check if a product exists by its ID."""
        product = self.find(product_id)  
        return product is not None