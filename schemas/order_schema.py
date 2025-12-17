from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from pydantic import Field, BaseModel, validator

if TYPE_CHECKING:
    from schemas.order_detail_schema import OrderDetailSchema


class OrderBaseSchema(BaseModel):
    client_id: int = Field(..., description="Client ID")
    bill_id: int | None = Field(None, description="Bill ID")
    total: float = Field(..., gt=0, description="Order total")
    delivery_method: int = Field(1, description="Delivery method: 1=Standard, 2=Pickup, 3=Express")
    status: int | None = Field(1, description="Order status: 1=Pending, 2=Processing, 3=Completed, 4=Cancelled")
    notes: str | None = Field(None, max_length=500, description="Order notes")

    class Config:
        from_attributes = True


class OrderDetailInOrderSchema(BaseModel):
    """Schema for order details inside OrderCreateSchema"""
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    price: float | None = Field(None, gt=0)

    class Config:
        from_attributes = True


class OrderCreateSchema(BaseModel):
    client_id: int = Field(..., description="Client ID")
    bill_id: int | None = None
    total: float = Field(..., gt=0, description="Order total")
    delivery_method: int = Field(1, ge=1, le=3, description="Delivery method: 1=Standard, 2=Pickup, 3=Express")
    status: int | None = Field(1, ge=1, le=4, description="Order status: 1=Pending, 2=Processing, 3=Completed, 4=Cancelled")
    notes: str | None = Field(None, max_length=500, description="Order notes")
    address: str | None = Field(None, max_length=500, description="Delivery address (required for Standard/Express delivery)")  # <-- Campo nuevo
    order_details: List[OrderDetailInOrderSchema] | None = Field(default_factory=list, description="Order items")

    @validator('total')
    def validate_total(cls, v):
        if v <= 0:
            raise ValueError('Total must be greater than 0')
        return round(v, 2)

    class Config:
        from_attributes = True

    @validator('total')
    def validate_total(cls, v):
        if v <= 0:
            raise ValueError('Total must be greater than 0')
        return round(v, 2)

    class Config:
        from_attributes = True


class OrderUpdateSchema(BaseModel):
    """Schema for updating an order."""
    client_id: int | None = Field(None, description="Client ID")
    bill_id: int | None = Field(None, description="Bill ID")
    total: float | None = Field(None, gt=0, description="Order total")
    delivery_method: int | None = Field(None, description="Delivery method")
    status: int | None = Field(None, description="Order status")
    notes: str | None = Field(None, max_length=500, description="Order notes")
    
    class Config:
        from_attributes = True


class OrderSchema(OrderBaseSchema):
    id_key: int
    order_number: str | None = None
    date: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True