from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from schemas.order_schema import OrderSchema
    from schemas.product_schema import ProductSchema


class OrderDetailBase(BaseModel):
    """Base schema for order details."""
    product_id: int = Field(..., gt=0, description="Product ID")
    quantity: int = Field(..., gt=0, description="Quantity")
    price: float = Field(..., gt=0, description="Unit price")
    
    class Config:
        from_attributes = True


class OrderDetailCreateSchema(BaseModel):
    """Schema for creating order details."""
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    price: float | None = Field(None, gt=0)

    class Config:
        from_attributes = True


class OrderDetailUpdateSchema(BaseModel):
    """Schema for updating order details."""
    product_id: int |None = Field(None, gt=0)
    quantity: int |None = Field(None, gt=0)
    price: float | None = Field(None, gt=0)
    
    class Config:
        from_attributes = True


class OrderDetailSchema(OrderDetailBase):
    """Complete order detail schema."""
    id_key: int
    order_id: int
    product_name: str |None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    
    # Relaciones opcionales
    order: OrderSchema | None = None
    product: ProductSchema | None = None
    
    class Config:
        from_attributes = True