from __future__ import annotations
from typing import Optional, List
from datetime import datetime
from pydantic import Field, BaseModel, EmailStr, SecretStr

class ClientBaseSchema(BaseModel):
    """Base schema for Client."""
    name: str = Field(..., min_length=1, max_length=100)
    lastname: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    company: Optional[str] = Field(None, max_length=100)
    tax_id: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None)
    # ❌ REMOVE: address: str | None = Field(None, max_length=500)

    class Config:
        from_attributes = True

class ClientCreateSchema(ClientBaseSchema):
    """Schema for creating Client."""
    pass

class ClientUpdateSchema(BaseModel):
    """Schema for updating Client."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    lastname: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    company: Optional[str] = Field(None, max_length=100)
    tax_id: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None)

    class Config:
        from_attributes = True

class ClientSchema(ClientBaseSchema):
    """Full Client schema."""
    id_key: int
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

ClientResponseSchema = ClientSchema

class ClientListResponseSchema(BaseModel):
    """Schema for returning a list of clients."""
    items: List[ClientSchema]
    total: int
    page: int
    size: int
    pages: int

    class Config:
        from_attributes = True

class ClientLoginSchema(BaseModel):
    """Schema for client login."""
    email: EmailStr
    password: SecretStr

class ClientRegisterSchema(BaseModel):
    email: EmailStr
    password: SecretStr
    confirm_password: SecretStr
    name: str = Field(..., min_length=2, max_length=50)
    lastname: str = Field(..., min_length=2, max_length=50)
    phone: str = Field(None, max_length=20)
    id_key: int = None  
    
    class Config:
        from_attributes = True

class ClientWithPasswordSchema(ClientSchema):
    """Client schema with password (for internal use only)."""
    password_hash: Optional[str] = None
    password_salt: Optional[str] = None

from pydantic import BaseModel

class DebugPasswordSchema(BaseModel):
    email: str
    password: str