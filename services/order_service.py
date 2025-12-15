"""OrderService with foreign key validation and business logic."""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
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
from schemas.order_schema import OrderCreateSchema, OrderSchema  # ✅ Agregar import

logger = get_sanitized_logger(__name__)

class OrderService(BaseServiceImpl):
    """Service for Order entity with validation and business logic."""

    def __init__(self, db: Session):
        super().__init__(
            repository_class=OrderRepository,
            model=OrderModel,
            schema=OrderSchema,  # ✅ Usar OrderSchema aquí
            db=db
        )
        self._client_repository = ClientRepository(db)
        self._bill_repository = BillRepository(db)

    def save(self, schema: 'OrderCreateSchema') -> 'OrderSchema':  # ✅ Cambiar tipo
        """
        Create a new order with validation

        Args:
            schema: OrderCreateSchema data

        Returns:
            Created order

        Raises:
            InstanceNotFoundError: If client doesn't exist
            ValueError: If validation fails
        """
        # Validar cliente
        try:
            self._client_repository.find(schema.client_id)
        except InstanceNotFoundError:
            logger.error(f"Client with id {schema.client_id} not found")
            raise InstanceNotFoundError(f"Client with id {schema.client_id} not found")

        # ✅ NO validar bill_id si es None (factura se creará después)
        if schema.bill_id:
            try:
                self._bill_repository.find(schema.bill_id)
            except InstanceNotFoundError:
                logger.error(f"Bill with id {schema.bill_id} not found")
                raise InstanceNotFoundError(f"Bill with id {schema.bill_id} not found")
        else:
            logger.info("Creating order without bill (will be generated later)")

        # Convertir OrderCreateSchema a OrderSchema
        order_data = {
            "client_id": schema.client_id,
            "bill_id": schema.bill_id,
            "total": schema.total,
            "delivery_method": schema.delivery_method,
            "status": schema.status,
            "notes": schema.notes if hasattr(schema, 'notes') else None,
            "date": datetime.utcnow(),
            # order_details se manejará por separado
        }
        
        # Filtrar valores None
        order_data = {k: v for k, v in order_data.items() if v is not None}
        
        # ✅ Crear orden sin order_details primero
        logger.info(f"Creating order for client {schema.client_id}")
        order_schema = OrderSchema(**order_data)
        return super().save(order_schema)

    def create_order_with_details(self, order_data: dict) -> 'OrderSchema':
        """
        Crear orden completa con detalles
        
        Args:
            order_data: Diccionario con client_id, total, order_details, etc.
            
        Returns:
            Order creada
        """
        # 1. Crear la orden base
        order_create = OrderCreateSchema(**order_data)
        order = self.save(order_create)
        
        # 2. Agregar order_details (si los hay)
        if order_data.get('order_details'):
            from services.order_detail_service import OrderDetailService
            order_detail_service = OrderDetailService(self.db)
            
            for detail in order_data['order_details']:
                detail_data = {
                    'order_id': order.id_key,
                    'product_id': detail.product_id,
                    'quantity': detail.quantity,
                    'price': detail.price
                }
                order_detail_service.save(detail_data)
        
        # 3. Generar factura automáticamente
        if not order_data.get('bill_id'):
            from services.bill_service import BillService
            bill_service = BillService(self.db)
            bill = bill_service.generate_bill_for_order(order.id_key)
            
            # Actualizar orden con bill_id
            order_update = {
                "bill_id": bill.id_key
            }
            order = self.update(order.id_key, OrderSchema(**order_update))
        
        return order

    def update(self, id_key: int, schema: 'OrderSchema') -> 'OrderSchema':
        """
        Update an order with validation

        Args:
            id_key: Order ID
            schema: Updated order data

        Returns:
            Updated order

        Raises:
            InstanceNotFoundError: If order, client, or bill doesn't exist
        """
        if schema.client_id is not None:
            try:
                self._client_repository.find(schema.client_id)
            except InstanceNotFoundError:
                logger.error(f"Client with id {schema.client_id} not found")
                raise InstanceNotFoundError(f"Client with id {schema.client_id} not found")

        if schema.bill_id is not None:
            try:
                self._bill_repository.find(schema.bill_id)
            except InstanceNotFoundError:
                logger.error(f"Bill with id {schema.bill_id} not found")
                raise InstanceNotFoundError(f"Bill with id {schema.bill_id} not found")

        logger.info(f"Updating order {id_key}")
        return super().update(id_key, schema)