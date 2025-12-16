from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from repositories.base_repository_impl import InstanceNotFoundError
from config.database_render import get_db
from schemas.order_schema import OrderCreateSchema, OrderUpdateSchema
from schemas.order_detail_schema import OrderDetailCreateSchema
from models.order import OrderModel
from services.order_service import OrderService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=Dict[str, Any], status_code=201)
def create_order(
    order_data: OrderCreateSchema,
    db: Session = Depends(get_db)
):
    """
    Create a new order with order details
    """
    try:
        logger.info(f"🔄 Creating order for client {order_data.client_id}")
        logger.info(f"📦 Order details count: {len(order_data.order_details)}")
        logger.info(f"🚚 Delivery method: {order_data.delivery_method}")

        order_service = OrderService(db)
        order_dict = order_data.model_dump()

        order_result = order_service.create_simple_order(order_dict)
        logger.info(f"✅ Order created successfully: {order_result['id_key']}")

        # Importación tardía para evitar circular imports
        from schemas.order_schema import OrderSchema
        return OrderSchema(**order_result)

    except ValueError as e:
        logger.error(f"❌ Validation error: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )
    except InstanceNotFoundError as e:
        logger.error(f"❌ Resource not found: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"💥 Unexpected error creating order: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/active", response_model=Dict[str, Any])
async def get_active_orders(db: Session = Depends(get_db)):
    """Obtener órdenes activas"""
    try:
        result = db.execute(text("""
            SELECT o.*, c.name as client_name
            FROM orders o
            LEFT JOIN clients c ON o.client_id = c.id
            WHERE o.status = 1
            ORDER BY o.date DESC
        """))

        active_orders = []
        for row in result:
            active_orders.append({
                "id": row.id,
                "date": row.date.isoformat() if hasattr(row.date, 'isoformat') else str(row.date),
                "total": row.total,
                "status": row.status,
                "client_id": row.client_id,
                "client_name": row.client_name or "Cliente"
            })

        return {
            "active_orders": active_orders,
            "count": len(active_orders)
        }
    except Exception as e:
        logger.error(f"Error en active orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{order_id}", response_model=Dict[str, Any])
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """Obtener una orden específica"""
    try:
        logger.info(f"Buscando orden con id_key: {order_id}")

        result = db.execute(text("""
            SELECT
                o.*,
                c.name as client_name,
                c.lastname as client_lastname,
                COALESCE(
                    json_agg(
                        json_build_object(
                            'product_id', od.product_id,
                            'quantity', od.quantity,
                            'price', od.price,
                            'product_name', p.name
                        )
                    ) FILTER (WHERE od.id_key IS NOT NULL),
                    '[]'::json
                ) as order_details
            FROM orders o
            LEFT JOIN clients c ON o.client_id = c.id
            LEFT JOIN order_details od ON o.id_key = od.order_id
            LEFT JOIN products p ON od.product_id = p.id
            WHERE o.id_key = :order_id
            GROUP BY o.id_key, c.name, c.lastname
        """), {"order_id": order_id})

        row = result.first()
        if not row:
            logger.warning(f"Orden {order_id} no encontrada")
            raise HTTPException(status_code=404, detail=f"Orden con ID {order_id} no encontrada")

        logger.info(f"Orden encontrada: {row.id_key}")

        return {
            "id_key": row.id_key,
            "id": row.id_key,
            "date": row.date.isoformat() if hasattr(row.date, 'isoformat') else str(row.date),
            "total": float(row.total) if row.total else 0.0,
            "delivery_method": row.delivery_method,
            "status": row.status,
            "client_id": row.client_id,
            "client_name": f"{row.client_name or ''} {row.client_lastname or ''}".strip(),
            "bill_id": row.bill_id,
            "created_at": row.created_at.isoformat() if hasattr(row.created_at, 'isoformat') else str(row.created_at),
            "updated_at": row.updated_at.isoformat() if hasattr(row.updated_at, 'isoformat') else str(row.updated_at),
            "order_details": row.order_details
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo orden {order_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error del servidor: {str(e)}")

@router.put("/{order_id}", response_model=Dict[str, Any])
async def update_order(
    order_id: int,
    order_data: OrderUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Actualizar una orden existente.
    """
    try:
        logger.info(f"Updating order ID {order_id}")

        order_service = OrderService(db)
        update_dict = order_data.model_dump(exclude_none=True)
        order = order_service.update(order_id, update_dict)

        # Importación tardía para evitar circular imports
        from schemas.order_schema import OrderSchema
        return order

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating order {order_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error updating order: {str(e)}"
        )
