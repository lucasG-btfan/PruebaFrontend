from __future__ import annotations
from datetime import datetime
from pydantic import Field, BaseModel


class ReviewBaseSchema(BaseModel):
    """Base schema for Review."""
    
    rating: float = Field(..., ge=1.0, le=5.0)
    comment: str | None = Field(None, min_length=10, max_length=1000)
    product_id: int = Field(...)
    
    class Config:
        from_attributes = True


class ReviewCreateSchema(ReviewBaseSchema):
    """Schema for creating Review."""
    pass


class ReviewUpdateSchema(BaseModel):
    """Schema for updating Review."""
    
    rating: float | None = Field(None, ge=1.0, le=5.0)
    comment: str | None = Field(None, min_length=10, max_length=1000)
    product_id: int | None = Field(None)
    
    class Config:
        from_attributes = True


class ReviewSchema(ReviewBaseSchema):
    """Full Review schema WITHOUT circular references."""
    
    id_key: int
    created_at: datetime | None = None
    updated_at: datetime | None = None  
    
    class Config:
        from_attributes = True