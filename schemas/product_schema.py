from __future__ import annotations
from typing import Optional, List
from datetime import datetime
from pydantic import Field, BaseModel


class ProductBaseSchema(BaseModel):
    """Base schema for Product."""
    
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    sku: Optional[str] = Field(None, max_length=100)
    category_id: Optional[int] = Field(None)
    
    class Config:
        from_attributes = True


class ProductCreateSchema(ProductBaseSchema):
    """Schema for creating Product."""
    pass


class ProductUpdateSchema(BaseModel):
    """Schema for updating Product."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    sku: Optional[str] = Field(None, max_length=100)
    category_id: Optional[int] = Field(None)
    
    class Config:
        from_attributes = True


class ProductSchema(ProductBaseSchema):
    """Full Product schema WITHOUT circular references."""
    
    id_key: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True