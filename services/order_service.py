"""OrderService simplified to avoid circular imports."""
from __future__ import annotations
from typing import Dict, Any, Optional
import logging
from sqlalchemy.orm import Session
from datetime import datetime

from models.order import OrderModel
from models.order_detail import OrderDetailModel
from repositories.order_repository import OrderRepository
from repositories.client_repository import ClientRepository
from repositories.bill_repository import BillRepository
from repositories.base_repository_impl import InstanceNotFoundError
from services.base_service_impl import BaseServiceImpl
from utils.logging_utils import get_sanitized_logger

logger = get_sanitized_logger(__name__)

class OrderService:
    """Service for Order entity - SIMPLIFIED VERSION."""

    def __init__(self, db: Session):
        self.db = db
        self._order_repo = OrderRepository(db)
        self._client_repo = ClientRepository(db)
        self._bill_repo = BillRepository(db)

    def create_simple_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a simple order without complex validation chains.
        
        Args:
            order_data: Dictionary with order data
            
        Returns:
            Created order as dict
        """
        try:
            client_id = order_data.get('client_id')
            if not client_id:
                raise ValueError("client_id is required")
                
            client = self._client_repo.find(client_id)
            if not client:
                raise InstanceNotFoundError(f"Client with id {client_id} not found")
            
            order_dict = {
                'client_id': client_id,
                'total': order_data.get('total', 0.0),
                'delivery_method': order_data.get('delivery_method', 1),
                'status': order_data.get('status', 1),
                'notes': order_data.get('notes', ''),
                'date': datetime.utcnow(),
                'bill_id': order_data.get('bill_id')
            }
            
            logger.info(f"Creating order for client {client_id}")
            
            order = self._save_simple(order_dict)
            order_details = order_data.get('order_details', [])
            if order_details:
                self._create_order_details(order.id_key, order_details)
            
            if not order_data.get('bill_id'):
                try:
                    bill = self._generate_bill(order.id_key)
                    order.bill_id = bill.id_key
                    self.db.commit()
                except Exception as bill_error:
                    logger.warning(f"Could not generate bill: {bill_error}")
            
            return self._order_to_dict(order)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating order: {e}", exc_info=True)
            raise

    def _save_simple(self, order_data: Dict[str, Any]) -> OrderModel:
        """Save order directly to database without complex schema validation."""
        order = OrderModel(**order_data)
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def _create_order_details(self, order_id: int, details: list):
        """Create order details."""
        for detail in details:
            order_detail = OrderDetailModel(
                order_id=order_id,
                product_id=detail.get('product_id'),
                quantity=detail.get('quantity', 1),
                price=detail.get('price', 0.0)
            )
            self.db.add(order_detail)
        self.db.commit()

    def _generate_bill(self, order_id: int):
        """Generate bill for order."""
        from services.bill_service import BillService
        
        bill_service = BillService(self.db)
        return bill_service.generate_bill_for_order(order_id)

    def _order_to_dict(self, order: OrderModel) -> Dict[str, Any]:
        """Convert OrderModel to dictionary."""
        return {
            'id_key': order.id_key,
            'client_id': order.client_id,
            'bill_id': order.bill_id,
            'total': float(order.total) if order.total else 0.0,
            'delivery_method': order.delivery_method,
            'status': order.status,
            'notes': order.notes,
            'date': order.date.isoformat() if order.date else None,
            'created_at': order.created_at.isoformat() if order.created_at else None,
            'updated_at': order.updated_at.isoformat() if order.updated_at else None
        }

    # Métodos básicos de CRUD
    def get(self, id_key: int) -> Dict[str, Any]:
        """Get order by ID."""
        order = self._order_repo.find(id_key)
        return self._order_to_dict(order)

    def update(self, id_key: int, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update order."""
        order = self._order_repo.find(id_key)
        
        for key, value in order_data.items():
            if hasattr(order, key) and value is not None:
                setattr(order, key, value)
        
        order.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(order)
        
        return self._order_to_dict(order)

    def delete(self, id_key: int) -> bool:
        """Delete order."""
        order = self._order_repo.find(id_key)
        self.db.delete(order)
        self.db.commit()
        return True