from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
from datetime import datetime

# Router para facturas
router = APIRouter(prefix="/api/v1/bills", tags=["Bills"])

# Mock data para desarrollo
mock_bills = [
    {
        "id": 1,
        "bill_number": "BILL-2024-001",
        "date": "2024-01-01",
        "total": 1499.97,
        "payment_type": 1,  # 1=CASH, 2=CREDIT_CARD, 3=DEBIT_CARD, 4=TRANSFER
        "client_id": 1,
        "discount": 0,
        "created_at": "2024-01-01T10:00:00Z"
    }
]

@router.post("", response_model=Dict[str, Any], status_code=201)
async def create_bill(bill_data: Dict[str, Any]):
    """Crear una nueva factura"""
    try:
        # Validación básica
        required_fields = ["bill_number", "date", "total", "payment_type", "client_id"]
        for field in required_fields:
            if field not in bill_data:
                raise HTTPException(status_code=400, detail=f"{field} is required")

        new_bill = {
            "id": len(mock_bills) + 1,
            **bill_data,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }

        mock_bills.append(new_bill)

        return {
            "message": "Bill created successfully",
            "bill_id": new_bill["id"],
            "bill": new_bill
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=Dict[str, Any])
async def get_bills(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Obtener lista de facturas"""
    return {
        "bills": mock_bills[skip:skip + limit],
        "total": len(mock_bills),
        "skip": skip,
        "limit": limit
    }

@router.get("/{bill_id}", response_model=Dict[str, Any])
async def get_bill(bill_id: int):
    """Obtener una factura específica"""
    bill = next((b for b in mock_bills if b["id"] == bill_id), None)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill
