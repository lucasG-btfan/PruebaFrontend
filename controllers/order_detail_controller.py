from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from config.database_render import get_db
from schemas.order_detail_schema import OrderDetailSchema, OrderDetailCreateSchema, OrderDetailUpdateSchema
from models.order_detail import OrderDetailModel
from models.order import OrderModel
from models.product import ProductModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/test")
async def test_order_details():
    return {"message": "Order details endpoint working"}

@router.get("", response_model=List[OrderDetailSchema])
async def get_order_details(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all order details with pagination."""
    try:
        order_details = db.query(OrderDetailModel).offset(skip).limit(limit).all()
        return order_details
    except Exception as e:
        logger.error(f"Error fetching order details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{order_detail_id}", response_model=OrderDetailSchema)
async def get_order_detail(order_detail_id: int, db: Session = Depends(get_db)):
    """Get order detail by ID."""
    order_detail = db.query(OrderDetailModel).filter(OrderDetailModel.id_key == order_detail_id).first()
    if not order_detail:
        raise HTTPException(status_code=404, detail="Order detail not found")
    return order_detail

@router.post("", response_model=OrderDetailSchema, status_code=status.HTTP_201_CREATED)
async def create_order_detail(
    order_detail_data: OrderDetailCreateSchema, 
    db: Session = Depends(get_db)
):
    """Create a new order detail."""
    try:
        # Verificar que la orden existe
        order = db.query(OrderModel).filter(OrderModel.id_key == order_detail_data.order_id).first()
        if not order:
            raise HTTPException(status_code=400, detail=f"Order with ID {order_detail_data.order_id} not found")
        
        # Verificar que el producto existe
        product = db.query(ProductModel).filter(ProductModel.id_key == order_detail_data.product_id).first()
        if not product:
            raise HTTPException(status_code=400, detail=f"Product with ID {order_detail_data.product_id} not found")
        
        # Verificar stock disponible
        if product.stock < order_detail_data.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient stock. Available: {product.stock}, Requested: {order_detail_data.quantity}"
            )
        
        # Actualizar stock del producto
        product.stock -= order_detail_data.quantity
        
        # Crear el detalle de orden
        order_detail_dict = order_detail_data.dict()
        order_detail = OrderDetailModel(**order_detail_dict)
        
        db.add(order_detail)
        db.commit()
        db.refresh(order_detail)
        
        return order_detail
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating order detail: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating order detail: {str(e)}")

@router.put("/{order_detail_id}", response_model=OrderDetailSchema)
async def update_order_detail(
    order_detail_id: int,
    order_detail_data: OrderDetailUpdateSchema,
    db: Session = Depends(get_db)
):
    """Update an order detail."""
    order_detail = db.query(OrderDetailModel).filter(OrderDetailModel.id_key == order_detail_id).first()
    if not order_detail:
        raise HTTPException(status_code=404, detail="Order detail not found")
    
    try:
        update_data = order_detail_data.dict(exclude_unset=True)
        
        # Manejo especial para cambios en cantidad
        old_quantity = order_detail.quantity
        new_quantity = update_data.get('quantity', old_quantity)
        
        if new_quantity != old_quantity:
            # Obtener el producto
            product_id = update_data.get('product_id', order_detail.product_id)
            product = db.query(ProductModel).filter(ProductModel.id_key == product_id).first()
            
            if not product:
                raise HTTPException(status_code=400, detail=f"Product with ID {product_id} not found")
            
            # Calcular diferencia y verificar stock
            quantity_diff = new_quantity - old_quantity
            if quantity_diff > 0 and product.stock < quantity_diff:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock. Available: {product.stock}, Additional needed: {quantity_diff}"
                )
            
            # Actualizar stock
            product.stock -= quantity_diff
        
        for key, value in update_data.items():
            if hasattr(order_detail, key):
                setattr(order_detail, key, value)
        
        db.commit()
        db.refresh(order_detail)
        return order_detail
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating order detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{order_detail_id}")
async def delete_order_detail(order_detail_id: int, db: Session = Depends(get_db)):
    """Delete an order detail and restore product stock."""
    order_detail = db.query(OrderDetailModel).filter(OrderDetailModel.id_key == order_detail_id).first()
    if not order_detail:
        raise HTTPException(status_code=404, detail="Order detail not found")
    
    try:
        # Restaurar stock del producto
        product = db.query(ProductModel).filter(ProductModel.id_key == order_detail.product_id).first()
        if product:
            product.stock += order_detail.quantity
        
        # Eliminar el detalle de orden
        db.delete(order_detail)
        db.commit()
        
        return {"message": "Order detail deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting order detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))