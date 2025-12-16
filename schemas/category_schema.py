"""Category schema with validation."""
from typing import Optional, List
from __future__ import annotations
from datetime import datetime
from pydantic import Field, BaseModel


class CategoryBaseSchema(BaseModel):
    """Base schema for Category."""
    
    name: str = Field(..., min_length=1, max_length=100)
    
    class Config:
        from_attributes = True


class CategoryCreateSchema(CategoryBaseSchema):
    """Schema for creating Category."""
    pass


class CategoryUpdateSchema(BaseModel):
    """Schema for updating Category."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    
    class Config:
        from_attributes = True


class CategorySchema(CategoryBaseSchema):
    """Full Category schema WITHOUT circular references."""
    
    id_key: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # REMOVER relación circular temporalmente
    # products: Optional[List[Dict]] = []
    
    class Config:
        from_attributes = True