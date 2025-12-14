"""Bill schema with validation."""
from datetime import date as DateType
from typing import Optional, TYPE_CHECKING
from pydantic import Field, validator
from datetime import datetime

from schemas.base_schema import BaseSchema
from models.enums import PaymentType

if TYPE_CHECKING:
    from schemas.order_schema import OrderSchema
    from schemas.client_schema import ClientSchema


class BillBase(BaseSchema):
    """Base schema for Bill."""
    
    bill_number: str = Field(..., min_length=1, max_length=50, description="Unique bill number")
    discount: Optional[float] = Field(0.0, ge=0, description="Discount amount")
    date: DateType = Field(default_factory=datetime.now().date, description="Bill date")
    total: float = Field(..., ge=0, description="Total amount")
    payment_type: PaymentType = Field(..., description="Payment type")
    client_id_key: int = Field(..., description="Client ID")  # Cambiado de client_id
    order_id_key: int = Field(..., description="Order ID")    # Agregado


class BillCreate(BillBase):
    """Schema for creating a new bill."""
    pass


class BillResponse(BillBase):
    """Schema for bill response."""
    
    id_key: int = Field(..., description="Bill ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")
    
    # Relaciones opcionales
    order: Optional['OrderSchema'] = None
    client: Optional['ClientSchema'] = None
    
    class Config:
        from_attributes = True  # Replaces orm_mode = True in Pydantic v2