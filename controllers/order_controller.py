from __future__ import annotations
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from schemas.order_schema import OrderCreateSchema, OrderUpdateSchema, OrderSchema, OrderResponseSchema
from services.order_service import OrderService
from config.database import get_db
from middleware.auth_middleware import get_current_user
from models.client import ClientModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/orders", response_model=OrderResponseSchema, status_code=201)
def create_order(
    order_data: OrderCreateSchema,
    current_user: ClientModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear una nueva orden."""
    try:
        logger.info(f"Creando nueva orden para usuario ID: {current_user.id_key}")

        # Asegurar que el client_id de la orden coincida con el usuario autenticado
        if order_data.client_id != current_user.id_key:
            logger.warning(f"Intento de crear orden para otro usuario. Orden: {order_data.client_id}, Usuario: {current_user.id_key}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes crear órdenes para otros usuarios"
            )

        order_service = OrderService(db)
        order_dict = order_data.model_dump()

        if not order_dict.get('order_details') or len(order_dict['order_details']) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La orden debe tener al menos un producto"
            )

        order_result = order_service.create_simple_order(order_dict)

        if not order_result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=order_result.get('error', 'Error desconocido')
            )

        # Asegúrate de que el resultado incluya el estado
        order_status = order_result.get('status', 1)  # Por defecto: 1 (Pendiente)

        return {
            "success": True,
            "message": order_result.get('message', 'Orden creada'),
            "order_id": order_result.get('order_id'),
            "bill_id": order_result.get('bill_id'),
            "client_id": current_user.id_key,
            "total": order_dict.get('total', 0.0),
            "status": order_status
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando orden para usuario {current_user.id_key}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@router.put("/orders/{order_id}", response_model=OrderSchema)
def update_order(
    order_id: int,
    order_data: OrderUpdateSchema,
    current_user: ClientModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar una orden existente."""
    try:
        logger.info(f"Actualizando orden ID {order_id} por usuario {current_user.id_key}")
        order_service = OrderService(db)
        update_dict = order_data.model_dump(exclude_none=True)

        # Verificar que la orden pertenece al usuario
        existing_order = order_service.get_order_by_id(order_id)
        if not existing_order or existing_order.client_id != current_user.id_key:
            logger.warning(f"Intento de actualizar orden no perteneciente. Orden: {order_id}, Usuario: {current_user.id_key}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes actualizar órdenes de otros usuarios"
            )

        order = order_service.update(order_id, update_dict)
        return order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando orden {order_id} por usuario {current_user.id_key}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando orden: {str(e)}"
        )

@router.get("/orders/active", response_model=Dict[str, Any])
def get_active_orders(
    current_user: ClientModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener órdenes activas del usuario autenticado."""
    try:
        order_service = OrderService(db)
        active_orders = order_service.get_active_orders_by_client(current_user.id_key)
        return {
            "active_orders": active_orders,
            "count": len(active_orders)
        }
    except Exception as e:
        logger.error(f"Error obteniendo órdenes activas para usuario {current_user.id_key}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/orders/{order_id}", response_model=OrderSchema)
def get_order(
    order_id: int,
    current_user: ClientModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener una orden específica del usuario autenticado."""
    try:
        logger.info(f"Buscando orden con id_key: {order_id} para usuario {current_user.id_key}")
        order_service = OrderService(db)
        order = order_service.get_order_by_id(order_id)

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Orden con ID {order_id} no encontrada"
            )

        if order.client_id != current_user.id_key:
            logger.warning(f"Intento de acceder a orden no perteneciente. Orden: {order_id}, Usuario: {current_user.id_key}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes acceder a órdenes de otros usuarios"
            )

        return order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo orden {order_id} para usuario {current_user.id_key}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error del servidor: {str(e)}"
        )
