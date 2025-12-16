from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from pydantic import Field, BaseModel, validator

if TYPE_CHECKING:
    from schemas.order_detail_schema import OrderDetailSchema


class OrderBaseSchema(BaseModel):
    client_id: int = Field(..., description="Client ID")
    bill_id: Optional[int] = Field(None, description="Bill ID")
    total: float = Field(..., gt=0, description="Order total")
    delivery_method: int = Field(1, description="Delivery method: 1=Standard, 2=Pickup, 3=Express")
    status: Optional[int] = Field(1, description="Order status: 1=Pending, 2=Processing, 3=Completed, 4=Cancelled")
    notes: Optional[str] = Field(None, max_length=500, description="Order notes")

    class Config:
        from_attributes = True


class OrderDetailInOrderSchema(BaseModel):
    """Schema for order details inside OrderCreateSchema"""
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    price: Optional[float] = Field(None, gt=0)

    class Config:
        from_attributes = True


class OrderCreateSchema(BaseModel):
    client_id: int = Field(..., description="Client ID")
    bill_id: Optional[int] = None
    total: float = Field(..., gt=0, description="Order total")
    delivery_method: int = Field(1, ge=1, le=3, description="Delivery method: 1=Standard, 2=Pickup, 3=Express")
    status: Optional[int] = Field(1, ge=1, le=4, description="Order status: 1=Pending, 2=Processing, 3=Completed, 4=Cancelled")
    notes: Optional[str] = Field(None, max_length=500, description="Order notes")
    order_details: Optional[List[OrderDetailInOrderSchema]] = Field(default_factory=list, description="Order items")

    @validator('total')
    def validate_total(cls, v):
        if v <= 0:
            raise ValueError('Total must be greater than 0')
        return round(v, 2)

    class Config:
        from_attributes = True


class OrderUpdateSchema(BaseModel):
    """Schema for updating an order."""
    client_id: Optional[int] = Field(None, description="Client ID")
    bill_id: Optional[int] = Field(None, description="Bill ID")
    total: Optional[float] = Field(None, gt=0, description="Order total")
    delivery_method: Optional[int] = Field(None, description="Delivery method")
    status: Optional[int] = Field(None, description="Order status")
    notes: Optional[str] = Field(None, max_length=500, description="Order notes")
    
    class Config:
        from_attributes = True


class OrderSchema(OrderBaseSchema):
    id_key: int
    order_number: Optional[str] = None
    date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True