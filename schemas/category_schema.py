"""Category schema with validation."""
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from pydantic import Field, BaseModel

if TYPE_CHECKING:
    from schemas.product_schema import ProductSchema


class CategoryBaseSchema(BaseModel):
    """Base schema for Category."""
    
    name: str = Field(..., min_length=1, max_length=100)
    
    class Config:
        from_attributes = True


class CategoryCreateSchema(CategoryBaseSchema):
    """Schema for creating Category."""
    pass


class CategoryUpdateSchema(BaseModel):
    """Schema for updating Category."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    
    class Config:
        from_attributes = True


class CategorySchema(CategoryBaseSchema):
    """Full Category schema with relationships."""
    
    id_key: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    products: Optional[List['ProductSchema']] = []
    
    class Config:
        from_attributes = True


# Actualiza las referencias después de definir la clase
CategorySchema.update_forward_refs()