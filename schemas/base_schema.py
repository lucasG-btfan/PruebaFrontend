from __future__ import annotations
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    """Base schema for all models."""
    
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }