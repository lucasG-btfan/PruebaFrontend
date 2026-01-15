from __future__ import annotations

# Product schemas
from schemas.product_schema import (
    ProductSchema,
    ProductCreateSchema,
    ProductUpdateSchema,
    ProductBaseSchema
)

# Client schemas
from schemas.client_schema import (
    ClientSchema,
    ClientCreateSchema,
    ClientUpdateSchema,
    ClientResponseSchema,
    ClientListResponseSchema
)

# Address schemas (separado del client)
from schemas.address_schema import (
    AddressSchema
)

# Order schemas
from schemas.order_schema import (
    OrderSchema,
    OrderCreateSchema,
    OrderUpdateSchema,
    OrderBaseSchema,
    OrderDetailInOrderSchema
)

# Order detail schemas
from schemas.order_detail_schema import (
    OrderDetailSchema,
    OrderDetailCreateSchema,
    OrderDetailUpdateSchema,
    OrderDetailBase,
    OrderDetailBaseSchema  # Esto debe existir en order_detail_schema.py
)

# Bill schemas
from schemas.bill_schema import (
    BillResponse,
    BillCreate,
    BillBase
)

# Category schemas
from schemas.category_schema import (
    CategorySchema,
    CategoryCreateSchema,
    CategoryUpdateSchema,
    CategoryBaseSchema
)

# Review schemas
from schemas.review_schema import (
    ReviewBase,
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    ProductReviewResponse
)

__all__ = [
    # Product
    'ProductSchema',
    'ProductCreateSchema',
    'ProductUpdateSchema',
    'ProductBaseSchema',
    # Client
    'ClientSchema',
    'ClientCreateSchema',
    'ClientUpdateSchema',
    'ClientResponseSchema',
    'ClientListResponseSchema',
    # Address
    'AddressSchema',
    # Order
    'OrderSchema',
    'OrderCreateSchema',
    'OrderUpdateSchema',
    'OrderBaseSchema',
    'OrderDetailInOrderSchema',
    # Order Detail
    'OrderDetailSchema',
    'OrderDetailCreateSchema',
    'OrderDetailUpdateSchema',
    'OrderDetailBase',
    'OrderDetailBaseSchema',
    # Bill
    'BillResponse',
    'BillCreate',
    'BillBase',
    # Category
    'CategorySchema',
    'CategoryCreateSchema',
    'CategoryUpdateSchema',
    'CategoryBaseSchema',
    # Review
    'ReviewBase',
    'ReviewCreate',
    'ReviewUpdate',
    'ReviewResponse',
    'ProductReviewResponse',
]