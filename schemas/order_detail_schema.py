"""OrderDetail schema with validation."""
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from pydantic import Field, BaseModel

if TYPE_CHECKING:
    from schemas.order_schema import OrderSchema
    from schemas.product_schema import ProductSchema


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
    """Full OrderDetail schema with relationships."""
    
    id_key: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    order: Optional['OrderSchema'] = None
    product: Optional['ProductSchema'] = None
    
    class Config:
        from_attributes = True


# Para evitar importaciones circulares
from schemas.order_schema import OrderSchema
from schemas.product_schema import ProductSchema

OrderDetailSchema.update_forward_refs()