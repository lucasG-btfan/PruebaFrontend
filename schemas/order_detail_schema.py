from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime
from pydantic import Field, BaseModel

if TYPE_CHECKING:
    from schemas.product_schema import ProductSchema


class OrderDetailBase(BaseModel):
    """Base schema for OrderDetail."""
    
    quantity: int = Field(..., gt=0)
    price: float | None = Field(None, gt=0)
    order_id: int = Field(...)
    product_id: int = Field(...)
    
    class Config:
        from_attributes = True


class OrderDetailCreateSchema(BaseModel):
    order_id: int = Field(..., gt=0)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    price: float | None = Field(None, gt=0)

    class Config:
        from_attributes = True
        extra = 'ignore' 


class OrderDetailUpdateSchema(BaseModel):
    """Schema for updating OrderDetail."""
    
    quantity: int | None = Field(None, gt=0)
    price: float | None = Field(None, gt=0)
    order_id: int | None = Field(None)
    product_id: int | None = Field(None)
    
    class Config:
        from_attributes = True


class OrderDetailSchema(OrderDetailBase):
    """Full OrderDetail schema WITHOUT circular references."""
    
    id_key: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    
    class Config:
        from_attributes = True


# Alias para compatibilidad
OrderDetailBaseSchema = OrderDetailBase