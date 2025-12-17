from __future__ import annotations
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from config.database_render import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/bills", tags=["bills"])

@router.get("/order/{order_id}", response_model=Dict[str, Any])
async def get_bill_by_order(order_id: int, db: Session = Depends(get_db)):
    """Obtener factura de una orden específica"""
    try:
        logger.info(f"Buscando factura para orden {order_id}")

        order_result = db.execute(
            text("SELECT * FROM orders WHERE id_key = :order_id"),
            {"order_id": order_id}
        )
        order = order_result.first()
        
        if not order:
            logger.warning(f"Orden {order_id} no encontrada")
            raise HTTPException(
                status_code=404, 
                detail=f"Orden con ID {order_id} no encontrada"
            )

        # Buscar la factura
        bill_result = db.execute(
            text("""
                SELECT 
                    b.*,
                    c.name as client_name,
                    c.lastname as client_lastname,
                    c.email as client_email
                FROM bills b
                LEFT JOIN clients c ON b.client_id_key = c.id_key
                WHERE b.order_id_key = :order_id
            """),
            {"order_id": order_id}
        )
        bill = bill_result.first()
        
        if not bill:
            logger.warning(f"Factura no encontrada para orden {order_id}")
            # Si no hay factura, se generar una respuesta con datos básicos de la orden
            return {
                "order_id": order_id,
                "bill_number": f"PENDIENTE-{order_id}",
                "date": order.date.isoformat() if order.date else None,
                "subtotal": float(order.total) if order.total else 0.0,
                "discount": 0.0,
                "tax": 0.0,
                "total": float(order.total) if order.total else 0.0,
                "payment_type": "pending",
                "status": "pending",
                "client_info": {
                    "id": order.client_id,
                    "name": "Cliente",
                    "lastname": f"ID {order.client_id}"
                },
                "order_details": []
            }

        # Si hay factura se  obtiene los detalles de la orden
        details_result = db.execute(
            text("""
                SELECT 
                    od.*,
                    p.name as product_name,
                    p.description as product_description
                FROM order_details od
                LEFT JOIN products p ON od.product_id = p.id_key
                WHERE od.order_id = :order_id
            """),
            {"order_id": order_id}
        )
        details = [dict(row) for row in details_result]

        # respuesta
        return {
            "order_id": order_id,
            "bill_number": bill.bill_number,
            "date": bill.date.isoformat() if bill.date else None,
            "subtotal": float(bill.total) if bill.total else 0.0,
            "discount": float(bill.discount) if bill.discount else 0.0,
            "tax": 0.0,  # Puedes calcularlo si tienes el campo
            "total": float(bill.total) if bill.total else 0.0,
            "payment_type": bill.payment_type.value if hasattr(bill.payment_type, 'value') else str(bill.payment_type),
            "status": "paid" if bill.total and bill.total > 0 else "pending",
            "client_info": {
                "id": bill.client_id_key,
                "name": bill.client_name or "",
                "lastname": bill.client_lastname or "",
                "email": bill.client_email or ""
            },
            "order_details": details,
            "created_at": bill.created_at.isoformat() if bill.created_at else None,
            "generated": True
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo factura para orden {order_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error del servidor al obtener factura: {str(e)}"
        )