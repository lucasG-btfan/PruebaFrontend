"""OrderService with foreign key validation and business logic."""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Dict, Any
import logging
from sqlalchemy.orm import Session
from datetime import datetime

from models.order import OrderModel
from repositories.order_repository import OrderRepository
from repositories.client_repository import ClientRepository
from repositories.bill_repository import BillRepository
from repositories.base_repository_impl import InstanceNotFoundError
from services.base_service_impl import BaseServiceImpl
from utils.logging_utils import get_sanitized_logger

logger = get_sanitized_logger(__name__)

class OrderService(BaseServiceImpl):
    """Service for Order entity with validation and business logic."""

    def __init__(self, db: Session):
        from schemas.order_schema import OrderSchema
        
        super().__init__(
            repository_class=OrderRepository,
            model=OrderModel,
            schema=OrderSchema, 
            db=db
        )
        self._client_repository = ClientRepository(db)
        self._bill_repository = BillRepository(db)

    def save(self, schema_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new order with validation

        Args:
            schema_data: Order data to create (dict)

        Returns:
            Created order

        Raises:
            InstanceNotFoundError: If client doesn't exist
            ValueError: If validation fails
        """
        from schemas.order_schema import OrderCreateSchema, OrderSchema
        
        order_create = OrderCreateSchema(**schema_data)
        
        try:
            self._client_repository.find(order_create.client_id)
        except InstanceNotFoundError:
            logger.error(f"Client with id {order_create.client_id} not found")
            raise InstanceNotFoundError(f"Client with id {order_create.client_id} not found")

        if order_create.bill_id:
            try:
                self._bill_repository.find(order_create.bill_id)
            except InstanceNotFoundError:
                logger.error(f"Bill with id {order_create.bill_id} not found")
                raise InstanceNotFoundError(f"Bill with id {order_create.bill_id} not found")
        else:
            logger.info("Creating order without bill (will be generated later)")

        
        order_dict = order_create.model_dump(exclude={'order_details'})
        order_dict['date'] = datetime.utcnow()
        order_dict = {k: v for k, v in order_dict.items() if v is not None}
        
        logger.info(f"Creating order for client {order_create.client_id}")
        order_schema = OrderSchema(**order_dict)
        return super().save(order_schema)

    def create_order_with_details(self, order_data: dict) -> Dict[str, Any]:
        """
        Crear orden completa con detalles
        
        Args:
            order_data: Diccionario con client_id, total, order_details, etc.
            
        Returns:
            Order creada
        """
        from schemas.order_schema import OrderCreateSchema, OrderSchema
        
        try:
            
            order_create = OrderCreateSchema(**order_data)
            order = self.save(order_data)  
            
            if order_data.get('order_details'):
                try:
                    from services.order_detail_service import OrderDetailService
                    order_detail_service = OrderDetailService(self.db)
                    
                    for detail in order_data['order_details']:
                        detail_data = {
                            'order_id': order.id_key,
                            'product_id': detail.get('product_id'),
                            'quantity': detail.get('quantity', 1),
                            'price': detail.get('price', 0.0)
                        }
                        order_detail_service.save(detail_data)
                except ImportError as e:
                    logger.warning(f"No se pudo importar OrderDetailService: {e}")
                    logger.info("Continuando sin detalles de orden por ahora")

            if not order_data.get('bill_id'):
                try:
                    from services.bill_service import BillService
                    bill_service = BillService(self.db)
                    bill = bill_service.generate_bill_for_order(order.id_key)
                    
                    # Actualizar orden con bill_id
                    update_data = {"bill_id": bill.id_key}
                    order = self.update(order.id_key, update_data)
                except ImportError as e:
                    logger.warning(f"No se pudo generar factura automática: {e}")
                    logger.info("Continuando sin factura por ahora")
            
            return order
            
        except Exception as e:
            logger.error(f"Error creating order with details: {e}")
            raise

    def update(self, id_key: int, schema_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an order with validation

        Args:
            id_key: Order ID
            schema_data: Updated order data (dict)

        Returns:
            Updated order

        Raises:
            InstanceNotFoundError: If order, client, or bill doesn't exist
        """
        from schemas.order_schema import OrderUpdateSchema, OrderSchema
        
        # Validar
        order_update = OrderUpdateSchema(**schema_data)
        
        if order_update.client_id is not None:
            try:
                self._client_repository.find(order_update.client_id)
            except InstanceNotFoundError:
                logger.error(f"Client with id {order_update.client_id} not found")
                raise InstanceNotFoundError(f"Client with id {order_update.client_id} not found")

        if order_update.bill_id is not None:
            try:
                self._bill_repository.find(order_update.bill_id)
            except InstanceNotFoundError:
                logger.error(f"Bill with id {order_update.bill_id} not found")
                raise InstanceNotFoundError(f"Bill with id {order_update.bill_id} not found")

        logger.info(f"Updating order {id_key}")
        order_schema = OrderSchema(**order_update.model_dump(exclude_none=True))
        return super().update(id_key, order_schema)