from __future__ import annotations
from sqlalchemy.orm import Session
from models.order import OrderModel
from repositories.base_repository_impl import BaseRepositoryImpl

class OrderRepository(BaseRepositoryImpl):
    """Repository for Order entity database operations."""

    def __init__(self, db: Session):
        from schemas.order_schema import OrderSchema
        super().__init__(OrderModel, OrderSchema, db)