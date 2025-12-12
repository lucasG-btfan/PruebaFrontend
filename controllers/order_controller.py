from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from config.database import get_db
from schemas.order_schema import OrderSchema, OrderCreateSchema
from models.order import OrderModel
from models.client import ClientModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])

@router.get("", response_model=Dict[str, Any])
async def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Obtener lista de órdenes usando SQL directo"""
    try:
        result = db.execute(text("""
            SELECT o.*,
                   json_agg(
                       json_build_object(
                           'product_id', od.product_id,
                           'quantity', od.quantity,
                           'price', od.price
                       )
                   ) as order_details
            FROM orders o
            LEFT JOIN order_details od ON o.id = od.order_id
            GROUP BY o.id
            ORDER BY o.date DESC
            LIMIT :limit OFFSET :skip
        """), {"limit": limit, "skip": skip})

        orders = []
        for row in result:
            orders.append({
                "id": row.id,
                "date": row.date,
                "total": row.total,
                "delivery_method": row.delivery_method,
                "status": row.status,
                "client_id": row.client_id,
                "bill_id": row.bill_id,
                "order_details": row.order_details if row.order_details[0]['product_id'] else []
            })

        count_result = db.execute(text("SELECT COUNT(*) as total FROM orders"))
        total = count_result.scalar()

        return {
            "orders": orders,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    except Exception as e:
        logger.error(f"Error en get_orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreateSchema,
    db: Session = Depends(get_db)
):
    """Crear una nueva orden"""
    try:
        logger.info(f"Recibiendo orden: {order_data}")

        # Validar existencia del cliente
        client = db.query(ClientModel).filter(ClientModel.id_key == order_data.client_id).first()
        if not client:
            raise HTTPException(status_code=400, detail=f"Cliente con ID {order_data.client_id} no encontrado")

        # Insertar la orden
        result = db.execute(text("""
            INSERT INTO orders (date, total, delivery_method, status, client_id, bill_id, order_number)
            VALUES (:date, :total, :delivery_method, :status, :client_id, :bill_id, :order_number)
            RETURNING id
        """), {
            "date": datetime.utcnow(),
            "total": order_data.total,
            "delivery_method": order_data.delivery_method,
            "status": 1,
            "client_id_key": order_data["client_id"],
            "bill_id": order_data.bill_id,
            "order_number": f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{OrderModel.get_next_order_number(db)}"
        })

        order_id = result.scalar()

        # Insertar detalles de la orden
        for detail in order_data.order_details:
            db.execute(text("""
                INSERT INTO order_details (order_id, product_id, quantity, price)
                VALUES (:order_id, :product_id, :quantity, :price)
            """), {
                "order_id": order_id,
                "product_id": detail.product_id,
                "quantity": detail.quantity,
                "price": detail.price
            })

        db.commit()

        return {
            "success": True,
            "message": "Orden creada exitosamente",
            "order_id": order_id,
            "order_number": f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{OrderModel.get_next_order_number(db)}",
            "created_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creando orden: {e}")
        raise HTTPException(status_code=500, detail=f"Error creando orden: {str(e)}")

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
        result = db.execute(text("""
            SELECT o.*,
                   json_agg(
                       json_build_object(
                           'product_id', od.product_id,
                           'quantity', od.quantity,
                           'price', od.price
                       )
                   ) as order_details
            FROM orders o
            LEFT JOIN order_details od ON o.id = od.order_id
            WHERE o.id = :order_id
            GROUP BY o.id
        """), {"order_id": order_id})

        row = result.first()
        if not row:
            raise HTTPException(status_code=404, detail="Orden no encontrada")

        return {
            "id": row.id,
            "date": row.date.isoformat() if hasattr(row.date, 'isoformat') else str(row.date),
            "total": row.total,
            "delivery_method": row.delivery_method,
            "status": row.status,
            "client_id": row.client_id,
            "bill_id": row.bill_id,
            "order_number": row.order_number,
            "order_details": row.order_details if row.order_details[0]['product_id'] else []
        }
    except Exception as e:
        logger.error(f"Error obteniendo orden {order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
