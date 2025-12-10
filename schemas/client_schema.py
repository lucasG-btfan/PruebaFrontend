# schemas/client_schema.py
"""
Pydantic schemas for Client.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

from schemas.base_schema import BaseSchema


class ClientBaseSchema(BaseSchema):
    """Base schema for Client."""
    name: str = Field(..., min_length=1, max_length=100)  # ← nombre
    lastname: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., description="Email address of the client")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    company: Optional[str] = Field(None, max_length=100, description="Company name")
    tax_id: Optional[str] = Field(None, max_length=50, description="Tax ID")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")
    is_active: bool = Field(default=True, description="Whether the client is active")

class ClientCreateSchema(ClientBaseSchema):
    """Schema for creating a new client."""
    pass


class ClientUpdateSchema(BaseSchema):
    """Schema for updating an existing client."""
    name: str = Field(..., min_length=1, max_length=100)  # ← nombre
    lastname: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = Field(None)
    phone: Optional[str] = Field(None, max_length=20)
    company: Optional[str] = Field(None, max_length=100)
    tax_id: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = Field(None)


class ClientResponseSchema(ClientBaseSchema):
    """Schema for client response."""
    id_key: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ALIAS para compatibilidad con importaciones existentes
ClientSchema = ClientResponseSchema  # <-- AÑADIR ESTO


class ClientListResponseSchema(BaseModel):
    """Schema for list of clients response."""
    items: List[ClientResponseSchema]
    total: int
    page: int
    size: int
    pages: int