from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from pydantic import Field, BaseModel

if TYPE_CHECKING:
    from .order_schema import OrderSchema

class OrderDetailBaseSchema(BaseModel):
    """Base schema for OrderDetail."""
    
    quantity: int = Field(..., gt=0)
    price: Optional[float] = Field(None, gt=0)
    order_id: int = Field(...)
    product_id: int = Field(...)
    
    class Config:
        from_attributes = True


class OrderDetailCreateSchema(BaseModel):
    order_id: int = Field(..., gt=0)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    price: Optional[float] = Field(None, gt=0)

    class Config:
        from_attributes = True
        extra = 'ignore' 


class OrderDetailUpdateSchema(BaseModel):
    """Schema for updating OrderDetail."""
    
    quantity: Optional[int] = Field(None, gt=0)
    price: Optional[float] = Field(None, gt=0)
    order_id: Optional[int] = Field(None)
    product_id: Optional[int] = Field(None)
    
    class Config:
        from_attributes = True


class OrderDetailSchema(OrderDetailBaseSchema):
    """Full OrderDetail schema WITHOUT circular references."""
    
    id_key: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True