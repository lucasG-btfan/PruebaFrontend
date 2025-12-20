from __future__ import annotations
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from schemas.order_schema import OrderCreateSchema, OrderUpdateSchema, OrderSchema
from services.order_service import OrderService
from config.database_render import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter() 

@router.post("/orders", response_model=Dict[str, Any], status_code=201)
def create_order(
    order_data: OrderCreateSchema,
    db: Session = Depends(get_db)
):
    """Crear una nueva orden."""
    try:
        logger.info(f"Creando nueva orden para cliente: {order_data.client_id}")
        
        order_service = OrderService(db)
        order_dict = order_data.model_dump()

        if not order_dict.get('client_id'):
            raise HTTPException(status_code=400, detail="client_id es requerido")

        if not order_dict.get('order_details') or len(order_dict['order_details']) == 0:
            raise HTTPException(status_code=400, detail="La orden debe tener al menos un producto")

        order_result = order_service.create_simple_order(order_dict)
        
        if not order_result.get('success'):
            raise HTTPException(status_code=400, detail=order_result.get('error', 'Error desconocido'))
        
        # Retornar respuesta compatible
        return {
            "success": True,
            "message": order_result.get('message', 'Orden creada'),
            "order_id": order_result.get('order_id'),
            "bill_id": order_result.get('bill_id'),
            "client_id": order_dict['client_id'],
            "total": order_dict.get('total', 0.0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando orden: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/orders/active", response_model=Dict[str, Any])
def get_active_orders(db: Session = Depends(get_db)):
    """Obtener órdenes activas."""
    try:
        order_service = OrderService(db)
        active_orders = order_service.get_active_orders()
        return {
            "active_orders": active_orders,
            "count": len(active_orders)
        }
    except Exception as e:
        logger.error(f"Error obteniendo órdenes activas: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders/{order_id}", response_model=OrderSchema)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Obtener una orden específica."""
    try:
        logger.info(f"Buscando orden con id_key: {order_id}")
        order_service = OrderService(db)
        order = order_service.get_order_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Orden con ID {order_id} no encontrada")
        return order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo orden {order_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error del servidor: {str(e)}")

@router.put("/orders/{order_id}", response_model=OrderSchema)
def update_order(
    order_id: int,
    order_data: OrderUpdateSchema,
    db: Session = Depends(get_db)
):
    """Actualizar una orden existente."""
    try:
        logger.info(f"Actualizando orden ID {order_id}")
        order_service = OrderService(db)
        update_dict = order_data.model_dump(exclude_none=True)
        order = order_service.update(order_id, update_dict)
        return order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando orden {order_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error actualizando orden: {str(e)}")
