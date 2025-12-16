from __future__ import annotations
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class AddressSchema(BaseModel):
    id_key: int
    street: str
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None

    class Config:
        from_attributes = True

class ClientBaseSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    lastname: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., description="Email address of the client")
    phone: str | None = Field(None, max_length=20, description="Phone number")
    company: str | None = Field(None, max_length=100, description="Company name")
    tax_id: str | None = Field(None, max_length=50, description="Tax ID")
    notes: str | None = Field(None, max_length=500, description="Additional notes")
    is_active: bool = Field(default=True, description="Whether the client is active")

    class Config:
        from_attributes = True

class ClientCreateSchema(ClientBaseSchema):
    address: str | None = Field(None, max_length=200, description="Client address as a single string")

class ClientUpdateSchema(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    lastname: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = Field(None)
    phone: str | None = Field(None, max_length=20)
    company: str | None = Field(None, max_length=100)
    tax_id: str | None = Field(None, max_length=50)
    notes: str | None = Field(None, max_length=500)
    is_active: bool | None = Field(None)
    address: str | None = Field(None, max_length=200, description="Client address as a single string")

    class Config:
        from_attributes = True

class ClientResponseSchema(ClientBaseSchema):
    id_key: int
    name: str
    lastname: str
    email: EmailStr
    phone: str | None = None
    company: str | None = None
    tax_id: str | None = None
    notes: str | None = None
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    addresses: Optional[List[AddressSchema]] = None

    class Config:
        from_attributes = True

class ClientListResponseSchema(BaseModel):
    items: List[ClientResponseSchema]
    total: int
    page: int
    size: int
    pages: int

    class Config:
        from_attributes = True

ClientSchema = ClientResponseSchema