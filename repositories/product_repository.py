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

    def get_by_id(self, product_id: int) -> Optional[ProductModel]:
        """Get a product by its ID."""
        return self.db.query(ProductModel).filter(
            ProductModel.id_key == product_id
        ).first()

    def exists(self, product_id: int) -> bool:
        """Check if a product exists by its ID."""
        product = self.get_by_id(product_id)
        return product is not None
