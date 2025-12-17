from __future__ import annotations
from typing import Optional, List
from datetime import datetime
from pydantic import Field, BaseModel, EmailStr

class ClientBaseSchema(BaseModel):
    """Base schema for Client."""

    name: str = Field(..., min_length=1, max_length=200)
    lastname: str | None = Field(None, max_length=200)
    email: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=50)
    address: str | None = Field(None, max_length=500)

    class Config:
        from_attributes = True

class ClientCreateSchema(ClientBaseSchema):
    """Schema for creating Client."""
    pass

class ClientUpdateSchema(BaseModel):
    """Schema for updating Client."""

    name: str | None = Field(None, min_length=1, max_length=200)
    lastname: str | None = Field(None, max_length=200)
    email: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=50)
    address: str | None = Field(None, max_length=500)

    class Config:
        from_attributes = True

class ClientSchema(ClientBaseSchema):
    """Full Client schema WITHOUT circular references."""

    id_key: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True

class ClientResponseSchema(ClientSchema):
    """Schema for returning a client in API responses."""

    deleted_at: datetime | None = None
    is_active: bool = True

    class Config:
        from_attributes = True

class ClientListResponseSchema(BaseModel):
    """Schema for returning a list of clients in API responses."""

    items: List[ClientResponseSchema]
    total: int
    page: int
    size: int
    pages: int

    class Config:
        from_attributes = True
