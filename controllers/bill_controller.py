# controllers/bill_controller.py
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from config.database import get_db
from models.bill import Bill
from schemas.bill_schema import BillCreate, BillResponse
import services.bill_service as bill_service

router = APIRouter(prefix="/api/v1/bills", tags=["Bills"])

@router.post("", response_model=BillResponse, status_code=201)
async def create_bill(bill_data: BillCreate, db: Session = Depends(get_db)):
    """Crear una nueva factura"""
    try:
        bill = bill_service.create_bill(db, bill_data)
        return bill
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[BillResponse])
async def get_bills(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Obtener lista de facturas"""
    bills = bill_service.get_bills(db, skip=skip, limit=limit)
    return bills

@router.get("/{bill_id}", response_model=BillResponse)
async def get_bill(bill_id: int, db: Session = Depends(get_db)):
    """Obtener una factura específica"""
    bill = bill_service.get_bill_by_id(db, bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill

@router.get("/order/{order_id}", response_model=BillResponse)
async def get_bill_by_order(order_id: int, db: Session = Depends(get_db)):
    """Obtener factura por ID de orden"""
    bill = bill_service.get_bill_by_order_id(db, order_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found for this order")
    return bill