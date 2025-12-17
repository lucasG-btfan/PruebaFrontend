from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field
from datetime import datetime

class OrderDetailInOrderSchema(BaseModel):
    """Schema for order details inside OrderCreateSchema"""
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    price: float | None = Field(None, gt=0)

    class Config:
        from_attributes = True

class OrderCreateSchema(BaseModel):
    client_id: int = Field(..., description="Client ID")
    total: float = Field(..., gt=0, description="Order total")
    delivery_method: int = Field(1, ge=1, le=3, description="Delivery method: 1=Standard, 2=Pickup, 3=Express")
    status: int | None = Field(1, ge=1, le=4, description="Order status: 1=Pending, 2=Processing, 3=Completed, 4=Cancelled")
    notes: str | None = Field(None, max_length=500, description="Order notes")
    address: str = Field(..., min_length=5, description="Delivery address")  
    order_details: List[OrderDetailInOrderSchema] = Field(default_factory=list, description="Order items")

    class Config:
        from_attributes = True

class OrderUpdateSchema(BaseModel):
    """Schema for updating an order."""
    total: float | None = Field(None, gt=0, description="Order total")
    delivery_method: int | None = Field(None, description="Delivery method")
    status: int | None = Field(None, description="Order status")
    notes: str | None = Field(None, max_length=500, description="Order notes")
    address: str | None = Field(None, description="Delivery address")
    bill_id: int | None = Field(None, description="Bill ID")

    class Config:
        from_attributes = True

class OrderSchema(BaseModel):
    id_key: int
    client_id: int
    bill_id: int | None = None
    total: float
    delivery_method: int
    status: int
    notes: str | None = None
    address: str | None = None
    date: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
