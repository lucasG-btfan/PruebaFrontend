from __future__ import annotations
from sqlalchemy.orm import Session
from models.order import OrderModel
from repositories.base_repository_impl import BaseRepositoryImpl
from schemas.order_schema import OrderSchema

class OrderRepository(BaseRepositoryImpl):
    """Repository for Order entity database operations."""

    def __init__(self, db: Session):
        super().__init__(OrderModel, OrderSchema, db)
    
    def get_orders_by_client(self, client_id_key: int):
        return self.db.query(OrderModel).filter(
            OrderModel.client_id_key == client_id_key
        ).all()

    def find(self, id_key: int):
        """Find order by ID."""
        return self.db.query(self.model).filter(self.model.id_key == id_key).first()

    def find_all(self, skip: int = 0, limit: int = 100):
        """Find all orders."""
        return self.db.query(self.model).offset(skip).limit(limit).all()