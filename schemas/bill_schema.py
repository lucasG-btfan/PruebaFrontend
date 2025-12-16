"""Bill schema with validation."""
from __future__ import annotations
from datetime import date as DateType, datetime
from typing import TYPE_CHECKING
from pydantic import Field

from schemas.base_schema import BaseSchema
from models.enums import PaymentType

if TYPE_CHECKING:
    from schemas.order_schema import OrderSchema
    from schemas.client_schema import ClientSchema


class BillBase(BaseSchema):
    """Base schema for Bill."""
    
    bill_number: str = Field(..., min_length=1, max_length=50, description="Unique bill number")
    discount: float | None = Field(default=0.0, ge=0, description="Discount amount")
    date: DateType = Field(default_factory=lambda: datetime.now().date(), description="Bill date")
    total: float = Field(..., ge=0, description="Total amount")
    payment_type: PaymentType = Field(..., description="Payment type")
    client_id_key: int = Field(..., description="Client ID")  
    order_id_key: int = Field(..., description="Order ID")
    
    class Config:
        from_attributes = True


class BillCreate(BillBase):
    """Schema for creating a new bill."""
    pass


class BillResponse(BillBase):
    """Schema for bill response."""
    
    id_key: int = Field(..., description="Bill ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Update timestamp")
    
    # NO incluir relaciones circulares aquí
    # order: OrderSchema | None = None
    # client: ClientSchema | None = None
    
    class Config:
        from_attributes = True