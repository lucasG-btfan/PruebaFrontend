# schemas/client_schema.py
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class AddressSchema(BaseModel):
    id_key: int
    street: str
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None

    class Config:
        from_attributes = True

class ClientBaseSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    lastname: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., description="Email address of the client")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    company: Optional[str] = Field(None, max_length=100, description="Company name")
    tax_id: Optional[str] = Field(None, max_length=50, description="Tax ID")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")
    is_active: bool = Field(default=True, description="Whether the client is active")

    class Config:
        from_attributes = True

class ClientCreateSchema(ClientBaseSchema):
    address: Optional[str] = Field(None, max_length=200, description="Client address as a single string")

class ClientUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    lastname: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = Field(None)
    phone: Optional[str] = Field(None, max_length=20)
    company: Optional[str] = Field(None, max_length=100)
    tax_id: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = Field(None)
    address: Optional[str] = Field(None, max_length=200, description="Client address as a single string")

    class Config:
        from_attributes = True

class ClientResponseSchema(ClientBaseSchema):
    id_key: int
    name: str
    lastname: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    tax_id: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
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