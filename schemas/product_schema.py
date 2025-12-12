from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from pydantic import Field, BaseModel

if TYPE_CHECKING:
    from schemas.review_schema import ReviewSchema
    from schemas.category_schema import CategorySchema
    from schemas.order_detail_schema import OrderDetailSchema

class ProductBaseSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Product name (required)")
    description: Optional[str] = Field(None, max_length=2000, description="Product description")
    price: float = Field(..., gt=0, description="Product price (must be greater than 0, required)")
    stock: int = Field(..., ge=0, description="Product stock quantity (must be >= 0)")
    sku: Optional[str] = Field(None, max_length=100, description="Product SKU")
    category_id: Optional[int] = Field(None, description="Category ID reference")

    class Config:
        from_attributes = True

class ProductSchema(ProductBaseSchema):
    id_key: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    category: Optional["CategorySchema"] = None
    reviews: Optional[List["ReviewSchema"]] = []
    order_details: Optional[List["OrderDetailSchema"]] = []

    class Config:
        from_attributes = True

# Actualiza las referencias después de definir la clase
from schemas import review_schema, category_schema, order_detail_schema
ProductSchema.update_forward_refs()
