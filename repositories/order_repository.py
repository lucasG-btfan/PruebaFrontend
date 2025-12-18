from __future__ import annotations
from sqlalchemy.orm import Session
from models.order import OrderModel
from repositories.base_repository_impl import BaseRepositoryImpl

class OrderRepository(BaseRepositoryImpl):
    """Repository for Order entity database operations."""

    def __init__(self, db: Session):
        from schemas.order_schema import OrderSchema
        super().__init__(model=OrderModel, schema=OrderSchema, db=db)
        self.db = db  
        self.model = OrderModel  

    def find(self, id_key: int):
        """Find order by ID."""
        return self.db.query(OrderModel).filter(OrderModel.id_key == id_key).first()

    def find_all(self, skip: int = 0, limit: int = 100):
        """Find all orders."""
        return self.db.query(OrderModel).offset(skip).limit(limit).all()
