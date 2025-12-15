from typing import Optional, List
from datetime import datetime
from pydantic import Field, BaseModel, validator

class OrderBaseSchema(BaseModel):
    """Base schema for Order."""
    client_id: int = Field(..., description="Client ID")
    bill_id: Optional[int] = Field(None, description="Bill ID")
    total: float = Field(..., gt=0, description="Order total")
    delivery_method: int = Field(1, description="Delivery method: 1=Standard, 2=Pickup, 3=Express")
    status: Optional[int] = Field(1, description="Order status: 1=Pending, 2=Processing, 3=Completed, 4=Cancelled")
    notes: Optional[str] = Field(None, max_length=500, description="Order notes")
    
    class Config:
        from_attributes = True

class OrderDetailCreateSchema(BaseModel):
    """Schema for order detail creation."""
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    price: Optional[float] = Field(None, gt=0)

class OrderCreateSchema(BaseModel):
    """Schema for creating an order."""
    client_id: int = Field(..., description="Client ID")
    bill_id: Optional[int] = None
    total: float = Field(..., gt=0, description="Order total")
    delivery_method: int = Field(1, ge=1, le=3, description="Delivery method: 1=Standard, 2=Pickup, 3=Express")
    status: Optional[int] = Field(1, ge=1, le=4, description="Order status: 1=Pending, 2=Processing, 3=Completed, 4=Cancelled")
    notes: Optional[str] = Field(None, max_length=500, description="Order notes")
    order_details: Optional[List[OrderDetailCreateSchema]] = Field(default=[], description="Order items")
    
    @validator('total')
    def validate_total(cls, v):
        if v <= 0:
            raise ValueError('Total must be greater than 0')
        return round(v, 2)
    
    @validator('order_details')
    def validate_order_details(cls, v):
        if v and len(v) == 0:
            raise ValueError('Order must have at least one item')
        return v
    
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

# Actualizar referencias hacia adelante
OrderSchema.update_forward_refs()
