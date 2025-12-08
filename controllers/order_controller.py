from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from datetime import datetime

# Router para órdenes
router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])

# Mock data para desarrollo
mock_orders = [
    {
        "id": 1,
        "client_id": 1,
        "total_amount": 1499.97,
        "status": 1,  # 1=PENDING, 2=PROCESSING, 3=COMPLETED, 4=CANCELLED
        "delivery_method": 1,  # 1=STANDARD, 2=PICKUP, 3=EXPRESS
        "bill_id": 1,
        "created_at": "2024-01-01T10:00:00Z",
        "order_details": [
            {"id": 1, "order_id": 1, "product_id": 1, "quantity": 1, "price": 1299.99},
            {"id": 2, "order_id": 1, "product_id": 2, "quantity": 2, "price": 49.99}
        ]
    }
]

@router.get("", response_model=Dict[str, Any])
async def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Obtener lista de órdenes"""
    return {
        "orders": mock_orders[skip:skip + limit],
        "total": len(mock_orders),
        "skip": skip,
        "limit": limit
    }

@router.post("", response_model=Dict[str, Any], status_code=201)
async def create_order(order_data: Dict[str, Any]):
    """Crear una nueva orden"""
    try:
        # Validación básica
        required_fields = ["client_id", "total_amount", "delivery_method"]
        for field in required_fields:
            if field not in order_data:
                raise HTTPException(status_code=400, detail=f"{field} is required")

        # Crear bill automáticamente si no existe
        if 'bill_id' not in order_data or not order_data.get('bill_id'):
            order_data['bill_id'] = len(mock_orders) + 100  # Simulación de ID de factura

        new_order = {
            "id": len(mock_orders) + 1,
            **order_data,
            "status": order_data.get("status", 1),  # Default PENDING
            "created_at": datetime.utcnow().isoformat() + "Z",
            "order_details": order_data.get("order_details", [])
        }

        mock_orders.append(new_order)

        return {
            "message": "Order created successfully",
            "order_id": new_order["id"],
            "order": new_order
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active", response_model=Dict[str, Any])
async def get_active_orders():
    """Obtener órdenes activas (status = 1)"""
    active_orders = [o for o in mock_orders if o.get("status") == 1]
    return {
        "active_orders": active_orders,
        "count": len(active_orders)
    }

@router.get("/{order_id}", response_model=Dict[str, Any])
async def get_order(order_id: int):
    """Obtener una orden específica"""
    order = next((o for o in mock_orders if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
