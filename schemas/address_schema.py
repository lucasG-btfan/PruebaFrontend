from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AddressBaseSchema(BaseModel):
    street: str = Field(..., max_length=255)
    city: str = Field(..., max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=20)


class AddressCreateSchema(AddressBaseSchema):
    client_id_key: int


class AddressUpdateSchema(BaseModel):
    street: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=20)


class AddressSchema(AddressBaseSchema):
    id_key: int
    client_id_key: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True