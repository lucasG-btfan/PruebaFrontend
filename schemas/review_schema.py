from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ReviewBase(BaseModel):
    rating: float = Field(..., ge=1, le=5, description="Rating entre 1 y 5 estrellas")
    comment: Optional[str] = None
    product_id: int
    order_id: int

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    rating: Optional[float] = Field(None, ge=1, le=5)
    comment: Optional[str] = None

class ReviewResponse(ReviewBase):
    id_key: int
    client_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProductReviewResponse(BaseModel):
    id_key: int
    rating: float
    comment: Optional[str]
    client_name: str
    created_at: datetime
