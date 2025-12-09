from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from models.order import OrderModel, OrderDetailModel
from models.enums import DeliveryMethod, Status
from config.database import get_db

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])

@router.get("", response_model=Dict[str, Any])
async def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Obtener lista de órdenes desde la base de datos"""
    orders = db.query(OrderModel).offset(skip).limit(limit).all()
    return {
        "orders": [
            {
                "id": order.id_key,
                "date": order.date,
                "total": order.total,
                "delivery_method": order.delivery_method.value,
                "status": order.status.value,
                "client_id": order.client_id,
                "bill_id": order.bill_id,
                "order_details": [
                    {
                        "product_id": detail.product_id,
                        "quantity": detail.quantity,
                        "price": detail.price
                    }
                    for detail in order.order_details
                ]
            }
            for order in orders
        ],
        "total": db.query(OrderModel).count(),
        "skip": skip,
        "limit": limit
    }

@router.post("", response_model=Dict[str, Any], status_code=201)
async def create_order(
    order_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Crear una nueva orden en la base de datos"""
    try:
        # Validación básica
        required_fields = ["client_id", "total", "delivery_method"]
        for field in required_fields:
            if field not in order_data:
                raise HTTPException(status_code=400, detail=f"{field} is required")

        # Crear la orden
        new_order = OrderModel(
            date=datetime.utcnow(),
            total=order_data["total"],
            delivery_method=DeliveryMethod(order_data["delivery_method"]),
            status=Status.PENDING,  # Default
            client_id=order_data["client_id"],
            bill_id=order_data.get("bill_id")
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        # Crear los detalles de la orden
        for detail in order_data.get("order_details", []):
            order_detail = OrderDetailModel(
                order_id=new_order.id_key,
                product_id=detail["product_id"],
                quantity=detail["quantity"],
                price=detail["price"]
            )
            db.add(order_detail)

        db.commit()

        return {
            "message": "Order created successfully",
            "order_id": new_order.id_key,
            "order": {
                "id": new_order.id_key,
                "date": new_order.date,
                "total": new_order.total,
                "delivery_method": new_order.delivery_method.value,
                "status": new_order.status.value,
                "client_id": new_order.client_id,
                "bill_id": new_order.bill_id,
                "order_details": [
                    {
                        "product_id": detail.product_id,
                        "quantity": detail.quantity,
                        "price": detail.price
                    }
                    for detail in new_order.order_details
                ]
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active", response_model=Dict[str, Any])
async def get_active_orders(db: Session = Depends(get_db)):
    """Obtener órdenes activas (status = PENDING)"""
    active_orders = db.query(OrderModel).filter(OrderModel.status == Status.PENDING).all()
    return {
        "active_orders": [
            {
                "id": order.id_key,
                "date": order.date,
                "total": order.total,
                "status": order.status.value,
                "client_id": order.client_id,
                "client_name": order.client.name if order.client else "Unknown"
            }
            for order in active_orders
        ],
        "count": len(active_orders)
    }

@router.get("/{order_id}", response_model=Dict[str, Any])
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """Obtener una orden específica"""
    order = db.query(OrderModel).filter(OrderModel.id_key == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {
        "id": order.id_key,
        "date": order.date,
        "total": order.total,
        "delivery_method": order.delivery_method.value,
        "status": order.status.value,
        "client_id": order.client_id,
        "bill_id": order.bill_id,
        "order_details": [
            {
                "product_id": detail.product_id,
                "quantity": detail.quantity,
                "price": detail.price
            }
            for detail in order.order_details
        ]
    }
