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
            text("""
                SELECT 
                    o.*,
                    c.name as client_name,
                    c.lastname as client_lastname,
                    c.email as client_email,
                    c.phone as client_phone
                FROM orders o
                LEFT JOIN clients c ON o.client_id = c.id_key
                WHERE o.id_key = :order_id
            """),
            {"order_id": order_id}
        )
        order = order_result.first()
        
        if not order:
            logger.warning(f"Orden {order_id} no encontrada")
            raise HTTPException(
                status_code=404, 
                detail=f"Orden con ID {order_id} no encontrada"
            )

        from models.bill import BillModel
        bill = db.query(BillModel).filter(BillModel.order_id_key == order_id).first()
        
        details_result = db.execute(
            text("""
                SELECT 
                    od.*,
                    p.name as product_name,
                    p.description as product_description,
                    p.price as unit_price
                FROM order_details od
                LEFT JOIN products p ON od.product_id = p.id_key
                WHERE od.order_id = :order_id
            """),
            {"order_id": order_id}
        )
        details = []
        subtotal_from_details = 0.0
        
        for row in details_result:
            row_dict = dict(row)
            quantity = float(row_dict.get('quantity', 0))
            unit_price = float(row_dict.get('unit_price', 0))
            line_subtotal = quantity * unit_price
            row_dict['line_subtotal'] = line_subtotal
            subtotal_from_details += line_subtotal
            details.append(row_dict)

        TAX_RATE = 0.21  
        
        if not bill:
            logger.warning(f"Factura no encontrada para orden {order_id}")
            order_total = float(order.total) if order.total else subtotal_from_details
            subtotal = order_total / (1 + TAX_RATE)  
            tax_amount = subtotal * TAX_RATE
            
            return {
                "order_id": order_id,
                "bill_number": f"PENDIENTE-{order_id}",
                "date": order.date.isoformat() if order.date else None,
                "subtotal": round(subtotal, 2),
                "discount": float(order.discount) if hasattr(order, 'discount') and order.discount else 0.0,
                "tax_rate": TAX_RATE,
                "tax_amount": round(tax_amount, 2),
                "total": round(order_total, 2),
                "payment_type": "pending",
                "status": "pending",
                "client_info": {
                    "id": order.client_id,
                    "name": order.client_name or "Cliente",
                    "lastname": order.client_lastname or f"ID {order.client_id}",
                    "email": order.client_email or "",
                    "phone": order.client_phone or ""
                },
                "order_details": details,
                "generated": False
            }

        bill_total = float(bill.total) if bill.total else 0.0
        
        if bill_total > 0:
            subtotal_calculated = bill_total / (1 + TAX_RATE)
            tax_amount_calculated = bill_total - subtotal_calculated
        else:
            subtotal_calculated = 0.0
            tax_amount_calculated = 0.0
        
        from models.client import ClientModel
        client = db.query(ClientModel).filter(ClientModel.id_key == bill.client_id_key).first()

        response = {
            "order_id": order_id,
            "bill_id": bill.id_key,
            "bill_number": bill.bill_number,
            "date": bill.date.isoformat() if bill.date else None,
            "subtotal": round(subtotal_calculated, 2),
            "discount": float(bill.discount) if bill.discount else 0.0,
            "tax_rate": TAX_RATE,
            "tax_amount": round(tax_amount_calculated, 2),
            "total": round(bill_total, 2),
            "payment_type": bill.payment_type.value if hasattr(bill.payment_type, 'value') else str(bill.payment_type),
            "status": "paid" if bill_total > 0 else "pending",
            "client_info": {
                "id": bill.client_id_key,
                "name": client.name if client else "",
                "lastname": client.lastname if client else "",
                "email": client.email if client else "",
                "phone": client.phone if client else ""
            },
            "order_details": details,
            "created_at": bill.created_at.isoformat() if bill.created_at else None,
            "updated_at": bill.updated_at.isoformat() if bill.updated_at else None,
            "generated": True
        }
        
        logger.info(f"Factura {bill.bill_number} encontrada para orden {order_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo factura para orden {order_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error del servidor al obtener factura: {str(e)}"
        )