"""Product schema for request/response validation."""
from typing import Optional, List, TYPE_CHECKING
from pydantic import Field

from schemas.base_schema import BaseSchema

if TYPE_CHECKING:
    from schemas.category_schema import CategorySchema
    from schemas.order_detail_schema import OrderDetailSchema
    from schemas.review_schema import ReviewSchema


class ProductBase(BaseSchema):
    """Base schema for Product."""
    name: str = Field(..., min_length=1, max_length=200, description="Product name (required)")
    price: float = Field(..., gt=0, description="Product price (must be greater than 0, required)")
    stock: int = Field(default=0, ge=0, description="Product stock quantity (must be >= 0)")
    category_id: int = Field(..., description="Category ID reference (required)")


class ProductCreate(ProductBase):
    """Schema for creating a product."""
    pass


class ProductUpdate(ProductBase):
    """Schema for updating a product."""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Product name")
    price: Optional[float] = Field(None, gt=0, description="Product price")
    stock: Optional[int] = Field(None, ge=0, description="Product stock quantity")
    category_id: Optional[int] = Field(None, description="Category ID reference")


class ProductResponse(ProductBase):
    """Schema for product response."""
    id_key: Optional[int] = None
    category: Optional['CategorySchema'] = None
    reviews: Optional[List['ReviewSchema']] = []
    order_details: Optional[List['OrderDetailSchema']] = []


# Alias para compatibilidad
ProductSchema = ProductResponse