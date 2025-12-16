from __future__ import annotations
from typing import Optional
from pydantic import Field
from typing import Optional, List

from schemas.base_schema import BaseSchema


class AddressSchema(BaseSchema):
    """Schema for Address entity with validations."""

    street: str | None = Field(None, min_length=1, max_length=200, description="Street name")
    number: str | None = Field(None, max_length=20, description="Street number")
    city: str | None = Field(None, min_length=1, max_length=100, description="City name")
    client_id: int = Field(..., description="Client ID reference (required)")
