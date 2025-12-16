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
    sku: str | None = Field(None, max_length=100)
    category_id: int | None = Field(None)
    
    class Config:
        from_attributes = True


class ProductCreateSchema(ProductBaseSchema):
    """Schema for creating Product."""
    pass


class ProductUpdateSchema(BaseModel):
    """Schema for updating Product."""
    
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    price: float | None= Field(None, gt=0)
    stock: int | None = Field(None, ge=0)
    sku: str | None = Field(None, max_length=100)
    category_id: int | None = Field(None)
    
    class Config:
        from_attributes = True


class ProductSchema(ProductBaseSchema):
    """Full Product schema WITHOUT circular references."""
    
    id_key: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    
    class Config:
        from_attributes = True