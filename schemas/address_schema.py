from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AddressBaseSchema(BaseModel):
    address_type: str = Field(default='shipping', max_length=50)
    street: str = Field(..., max_length=255)
    city: str = Field(..., max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: str = Field(default='Argentina', max_length=100)
    is_default: bool = Field(default=False)

class AddressCreateSchema(AddressBaseSchema):
    client_id_key: int

class AddressUpdateSchema(BaseModel):
    address_type: Optional[str] = Field(None, max_length=50)
    street: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None

class AddressSchema(AddressBaseSchema):
    id_key: int
    client_id_key: int
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True