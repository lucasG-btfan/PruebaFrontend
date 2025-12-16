from __future__ import annotations
from datetime import datetime
from pydantic import Field, BaseModel
from typing import Optional, List

class ReviewBaseSchema(BaseModel):
    """Base schema for Review."""
    
    rating: float = Field(..., ge=1.0, le=5.0)
    comment: Optional[str] = Field(None, min_length=10, max_length=1000)
    product_id: int = Field(...)
    
    class Config:
        from_attributes = True


class ReviewCreateSchema(ReviewBaseSchema):
    """Schema for creating Review."""
    pass


class ReviewUpdateSchema(BaseModel):
    """Schema for updating Review."""
    
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    comment: Optional[str] = Field(None, min_length=10, max_length=1000)
    product_id: Optional[int] = Field(None)
    
    class Config:
        from_attributes = True


class ReviewSchema(ReviewBaseSchema):
    """Full Review schema WITHOUT circular references."""
    
    id_key: int
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True