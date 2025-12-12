"""Product schema for request/response validation."""
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from pydantic import Field, BaseModel

if TYPE_CHECKING:
    from schemas.category_schema import CategorySchema
    from schemas.order_detail_schema import OrderDetailSchema
    from schemas.review_schema import ReviewSchema

class ProductBaseSchema(BaseModel):
    """Base schema for Product."""

    name: str = Field(..., min_length=1, max_length=200, description="Product name (required)")
    description: Optional[str] = Field(None, max_length=2000, description="Product description")
    price: float = Field(..., gt=0, description="Product price (must be greater than 0, required)")
    stock: int = Field(..., ge=0, description="Product stock quantity (must be >= 0)")
    sku: Optional[str] = Field(None, max_length=100, description="Product SKU")
    category_id: Optional[int] = Field(None, description="Category ID reference")

    class Config:
        from_attributes = True

class ProductCreateSchema(ProductBaseSchema):
    """Schema for creating a product."""
    pass

class ProductUpdateSchema(BaseModel):
    """Schema for updating a product."""

    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Product name")
    description: Optional[str] = Field(None, max_length=2000, description="Product description")
    price: Optional[float] = Field(None, gt=0, description="Product price")
    stock: Optional[int] = Field(None, ge=0, description="Product stock quantity")
    sku: Optional[str] = Field(None, max_length=100, description="Product SKU")
    category_id: Optional[int] = Field(None, description="Category ID reference")

    class Config:
        from_attributes = True

class ProductSchema(ProductBaseSchema):
    """Full Product schema with relationships."""

    id_key: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    category: Optional['CategorySchema'] = None
    reviews: Optional[List['ReviewSchema']] = []
    order_details: Optional[List['OrderDetailSchema']] = []

    class Config:
        from_attributes = True

# Actualiza las referencias después de definir las clases
from schemas.category_schema import CategorySchema
from schemas.review_schema import ReviewSchema
from schemas.order_detail_schema import OrderDetailSchema

ProductSchema.update_forward_refs()
