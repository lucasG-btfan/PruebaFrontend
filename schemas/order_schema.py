from __future__ import annotations
from typing import List, TYPE_CHECKING
from datetime import datetime
from pydantic import Field, BaseModel, validator
from models.enums import DeliveryMethod, Status

if TYPE_CHECKING:
    from schemas.order_detail_schema import OrderDetailSchema

class OrderBaseSchema(BaseModel):
    client_id_key: int = Field(..., description="Client ID")
    bill_id: int | None = Field(None, description="Bill ID")
    total: float = Field(..., gt=0, description="Order total")
    delivery_method: DeliveryMethod = Field(..., description="Delivery method")
    status: Status = Field(..., description="Order status")
    address: str | None = Field(None, max_length=500, description="Delivery address")

    class Config:
        from_attributes = True
        populate_by_name = True

class OrderDetailInOrderSchema(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    price: float | None = Field(None, gt=0)

    class Config:
        from_attributes = True

class OrderCreateSchema(BaseModel):
    client_id_key: int = Field(..., description="Client ID")
    bill_id: int | None = None
    total: float = Field(..., gt=0, description="Order total")
    delivery_method: DeliveryMethod = Field(..., description="Delivery method")
    status: Status = Field(..., description="Order status")
    address: str | None = Field(None, max_length=500, description="Delivery address")
    order_details: List[OrderDetailInOrderSchema] = Field(default_factory=list, description="Order items")

    @validator('total')
    def validate_total(cls, v):
        if v <= 0:
            raise ValueError('Total must be greater than 0')
        return round(v, 2)

    class Config:
        from_attributes = True
        populate_by_name = True

class OrderUpdateSchema(BaseModel):
    client_id_key: int | None = Field(None, description="Client ID")
    bill_id: int | None = Field(None, description="Bill ID")
    total: float | None = Field(None, gt=0, description="Order total")
    delivery_method: DeliveryMethod | None = Field(None, description="Delivery method")
    status: Status | None = Field(None, description="Order status")
    address: str | None = Field(None, max_length=500, description="Delivery address")

    class Config:
        from_attributes = True

class OrderSchema(OrderBaseSchema):
    id_key: int
    date: datetime
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True

class OrderResponseSchema(BaseModel):
    id_key: int
    order_number: str
    client_id_key: int
    total: float
    delivery_method: DeliveryMethod
    status: Status
    address: str | None
    date: datetime
    created_at: datetime
    message: str = "Order created successfully"

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class OrderListSchema(BaseModel):
    id_key: int
    order_number: str
    client_id_key: int
    total: float
    status: Status
    date: datetime
    address: str | None

    class Config:
        from_attributes = True
