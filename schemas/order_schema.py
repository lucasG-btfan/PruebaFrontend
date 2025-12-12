"""Order schema with validation."""
from typing import Optional, List
from datetime import datetime
from pydantic import Field, BaseModel


class OrderBaseSchema(BaseModel):
    """Base schema for Order."""
    
    client_id: int = Field(...)
    bill_id: Optional[int] = Field(None)
    total_amount: float = Field(..., ge=0)
    status: int = Field(default=1, ge=1, le=4)  # 1-4 según OrderStatus
    delivery_method: int = Field(default=1, ge=1, le=3)  # 1-3 según DeliveryMethod
    notes: Optional[str] = Field(None, max_length=500)
    date: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OrderCreateSchema(OrderBaseSchema):
    """Schema for creating Order."""
    pass


class OrderUpdateSchema(BaseModel):
    """Schema for updating Order."""
    
    client_id: Optional[int] = Field(None)
    bill_id: Optional[int] = Field(None)
    total_amount: Optional[float] = Field(None, ge=0)
    status: Optional[int] = Field(None, ge=1, le=4)
    delivery_method: Optional[int] = Field(None, ge=1, le=3)
    notes: Optional[str] = Field(None, max_length=500)
    date: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OrderSchema(OrderBaseSchema):
    """Full Order schema."""
    
    id_key: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    order_number: Optional[str] = None
    
    class Config:
        from_attributes = True