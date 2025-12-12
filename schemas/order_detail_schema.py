# schemas/order_detail_schema.py
"""OrderDetail schema with validation."""
from typing import Optional
from datetime import datetime
from pydantic import Field, BaseModel


class OrderDetailBaseSchema(BaseModel):
    """Base schema for OrderDetail."""
    
    quantity: int = Field(..., gt=0)
    price: Optional[float] = Field(None, gt=0)
    order_id: int = Field(...)
    product_id: int = Field(...)
    
    class Config:
        from_attributes = True


class OrderDetailCreateSchema(OrderDetailBaseSchema):
    """Schema for creating OrderDetail."""
    pass


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