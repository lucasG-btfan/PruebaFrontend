"""Product service with Redis caching integration and sanitized logging."""
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from models.product import ProductModel
from schemas.product_schema import ProductSchema, ProductCreateSchema, ProductUpdateSchema 
from repositories.product_repository import ProductRepository
from services.base_service_impl import BaseServiceImpl
from services.cache_service import cache_service
from utils.logging_utils import get_sanitized_logger

logger = get_sanitized_logger(__name__)


class ProductService(BaseServiceImpl):
    """Service for Product entity with caching."""

    def __init__(self, db: Session):
        super().__init__(
            repository_class=ProductRepository,
            model=ProductModel,
            schema=ProductSchema,  
            db=db
        )
        self.cache = cache_service
        self.cache_prefix = "products"

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ProductSchema]: 
        """
        Get all products with caching
        """
        # Build cache key
        cache_key = self.cache.build_key(
            self.cache_prefix,
            "list",
            skip=skip,
            limit=limit
        )

        # Try to get from cache
        cached_products = self.cache.get(cache_key)
        if cached_products is not None:
            logger.debug(f"Cache HIT: {cache_key}")
            # Convert dict list back to ProductSchema list
            return [ProductSchema(**p) for p in cached_products]

        # Cache miss - get from database
        logger.debug(f"Cache MISS: {cache_key}")
        products = super().get_all(skip, limit)

        products_dict = [p.model_dump() for p in products]
        self.cache.set(cache_key, products_dict)

        return products

    def get_one(self, id_key: int) -> ProductSchema:  
        """
        Get single product by ID with caching
        """
        cache_key = self.cache.build_key(self.cache_prefix, "id", id=id_key)

        # Try cache first
        cached_product = self.cache.get(cache_key)
        if cached_product is not None:
            logger.debug(f"Cache HIT: {cache_key}")
            return ProductSchema(**cached_product)

        # Get from database
        logger.debug(f"Cache MISS: {cache_key}")
        product = super().get_one(id_key)

        # Cache the result
        self.cache.set(cache_key, product.model_dump())

        return product

    def save(self, schema: ProductCreateSchema) -> ProductSchema: 
        """
        Create new product and invalidate list cache
        """
        product = super().save(schema)

        # Invalidate list cache (all paginated lists)
        self._invalidate_list_cache()

        return product

    def update(self, id_key: int, schema: ProductUpdateSchema) -> ProductSchema: 
        """
        Update product with transactional cache invalidation
        """
        cache_key = self.cache.build_key(self.cache_prefix, "id", id=id_key)

        try:
            product = super().update(id_key, schema)

            self.cache.delete(cache_key)
            self._invalidate_list_cache()

            logger.info(f"Product {id_key} updated and cache invalidated successfully")
            return product

        except Exception as e:
            logger.error(f"Failed to update product {id_key}: {e}")
            raise

    def delete(self, id_key: int) -> None:
        """Delete product with validation"""
        from models.order_detail import OrderDetailModel
        from sqlalchemy import select

        stmt = select(OrderDetailModel).where(
            OrderDetailModel.product_id == id_key
        ).limit(1)

        has_sales = self._repository.session.scalars(stmt).first()

        if has_sales:
            logger.error(
                f"Cannot delete product {id_key}: has associated sales history"
            )
            raise ValueError(
                f"Cannot delete product {id_key}: product has associated sales history. "
                f"Consider marking as inactive instead of deleting."
            )

        logger.info(f"Deleting product {id_key} (no sales history)")
        super().delete(id_key)

        cache_key = self.cache.build_key(self.cache_prefix, "id", id=id_key)
        self.cache.delete(cache_key)

        self._invalidate_list_cache()

    def _invalidate_list_cache(self):
        """Invalidate all product list caches"""
        pattern = f"{self.cache_prefix}:list:*"
        deleted_count = self.cache.delete_pattern(pattern)
        if deleted_count > 0:
            logger.info(f"Invalidated {deleted_count} product list cache entries")