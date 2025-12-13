from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from config.database_render import get_db
from schemas.order_schema import OrderCreateSchema, OrderUpdateSchema
from models.order import OrderModel
from models.client import ClientModel
from models.enums import DeliveryMethod, Status
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Orders"])

@router.get("/test")
async def test_orders():
    return {"message": "Orders endpoint working ✅"}

@router.get("", response_model=Dict[str, Any])
async def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Obtener lista de órdenes"""
    try:
        result = db.execute(text("""
            SELECT 
                o.*,
                c.name as client_name,
                c.lastname as client_lastname,
                COUNT(od.id_key) as items_count
            FROM orders o
            LEFT JOIN clients c ON o.client_id_key = c.id_key
            LEFT JOIN order_details od ON o.id_key = od.order_id
            GROUP BY o.id_key, c.name, c.lastname
            ORDER BY o.date DESC NULLS LAST, o.created_at DESC
            LIMIT :limit OFFSET :skip
        """), {"limit": limit, "skip": skip})

        orders = []
        for row in result:
            orders.append({
                "id": row.id_key,
                "id_key": row.id_key,
                "date": row.date.isoformat() if hasattr(row.date, 'isoformat') else str(row.date),
                "total": float(row.total) if row.total else 0.0,
                "delivery_method": row.delivery_method,
                "status": row.status,
                "client_id": row.client_id_key,
                "client_id_key": row.client_id_key,
                "client_name": f"{row.client_name or ''} {row.client_lastname or ''}".strip(),
                "bill_id": row.bill_id,
                "items_count": row.items_count,
                "created_at": row.created_at.isoformat() if hasattr(row.created_at, 'isoformat') else str(row.created_at)
            })

        count_result = db.execute(text("SELECT COUNT(*) as total FROM orders"))
        total = count_result.scalar() or 0

        return {
            "orders": orders,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    except Exception as e:
        logger.error(f"Error en get_orders: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error del servidor: {str(e)}")

@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreateSchema,
    db: Session = Depends(get_db)
):
    """Crear una nueva orden"""
    try:
        logger.info(f"Recibiendo orden: {order_data.dict()}")

        client = db.query(ClientModel).filter(ClientModel.id_key == order_data.client_id).first()
        if not client:
            raise HTTPException(status_code=400, detail=f"Cliente con ID {order_data.client_id} no encontrado")

        try:
            delivery_method_name = DeliveryMethod(order_data.delivery_method).name
        except ValueError:
            delivery_method_name = DeliveryMethod.DRIVE_THRU.name
            logger.warning(f"Método de entrega inválido {order_data.delivery_method}, usando DRIVE_THRU por defecto")

        try:
            status_name = Status(order_data.status).name
        except ValueError:
            status_name = Status.PENDING.name
            logger.warning(f"Status inválido {order_data.status}, usando PENDING por defecto")

        now = datetime.utcnow()
        result = db.execute(text("""
            INSERT INTO orders (date, total, delivery_method, status, client_id_key, bill_id, created_at, updated_at)
            VALUES (:date, :total, :delivery_method, :status, :client_id_key, :bill_id, :created_at, :updated_at)
            RETURNING id_key
        """), {
            "date": now,
            "total": order_data.total,
            "delivery_method": delivery_method_name,
            "status": status_name,
            "client_id_key": order_data.client_id,
            "bill_id": order_data.bill_id,
            "created_at": now,
            "updated_at": now   
        })

        order_id = result.scalar()
        logger.info(f"Orden creada con ID: {order_id}")

        if hasattr(order_data, 'order_details') and order_data.order_details:
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
        else:
            logger.warning("No order_details provided")

        db.commit()

        return {
            "success": True,
            "message": "Orden creada exitosamente",
            "order_id": order_id,
            "id_key": order_id,
            "created_at": now.isoformat()
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creando orden: {e}", exc_info=True)
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
            LEFT JOIN clients c ON o.client_id_key = c.id_key
            LEFT JOIN order_details od ON o.id_key = od.order_id
            LEFT JOIN products p ON od.product_id = p.id_key
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
            "id": row.id_key,  # Para compatibilidad
            "date": row.date.isoformat() if hasattr(row.date, 'isoformat') else str(row.date),
            "total": float(row.total) if row.total else 0.0,
            "delivery_method": row.delivery_method,
            "status": row.status,
            "client_id": row.client_id_key,
            "client_id_key": row.client_id_key,
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
    Permite modificar: status, delivery_method, total, client_id, bill_id, notes.
    """
    try:
        logger.info(f"Actualizando orden ID {order_id} con datos: {order_data.model_dump()}")

        existing_order = db.execute(text("""
            SELECT id_key FROM orders WHERE id_key = :order_id
        """), {"order_id": order_id}).fetchone()

        if not existing_order:
            raise HTTPException(status_code=404, detail=f"Orden con ID {order_id} no encontrada")

        delivery_method_name = None
        if order_data.delivery_method is not None:
            try:
                delivery_method_name = DeliveryMethod(order_data.delivery_method).name
            except ValueError:
                delivery_method_name = DeliveryMethod.DRIVE_THRU.name
                logger.warning(f"Método de entrega inválido {order_data.delivery_method}, usando DRIVE_THRU por defecto")

        status_name = None
        if order_data.status is not None:
            try:
                status_name = Status(order_data.status).name
            except ValueError:
                status_name = Status.PENDING.name
                logger.warning(f"Status inválido {order_data.status}, usando PENDING por defecto")

        update_fields = {
            "updated_at": datetime.utcnow() 
        }

        if order_data.status is not None:
            update_fields["status"] = status_name

        if order_data.delivery_method is not None:
            update_fields["delivery_method"] = delivery_method_name

        if order_data.total is not None:
            update_fields["total"] = order_data.total

        if order_data.client_id is not None:
            update_fields["client_id_key"] = order_data.client_id

        if order_data.bill_id is not None:
            update_fields["bill_id"] = order_data.bill_id

        if order_data.notes is not None:
            update_fields["notes"] = order_data.notes

        set_clause = ", ".join([f"{key} = :{key}" for key in update_fields.keys()])
        query = f"""
            UPDATE orders
            SET {set_clause}
            WHERE id_key = :order_id
            RETURNING id_key
        """
        update_fields["order_id"] = order_id

        result = db.execute(text(query), update_fields)
        updated_order_id = result.scalar()

        if not updated_order_id:
            raise HTTPException(status_code=404, detail=f"No se pudo actualizar la orden con ID {order_id}")

        db.commit()

        return {
            "success": True,
            "message": f"Orden {order_id} actualizada exitosamente",
            "order_id": updated_order_id,
            "updated_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error actualizando orden {order_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error actualizando orden: {str(e)}")
