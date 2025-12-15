"""
Schemas package initialization.
Import schemas in a specific order to avoid circular dependencies.
"""

from .order_schema import (
    OrderDetailCreateSchema,
    OrderCreateSchema,
    OrderUpdateSchema,
    OrderSchema
)

from .bill_schema import (
    BillBase,
    BillCreate,
    BillResponse
)

from .order_detail_schema import(
    OrderDetailBaseSchema,
    OrderCreateSchema,
    OrderDetailUpdateSchema
)

from .product_schema import(
    ProductBaseSchema,
    ProductSchema,
    ProductCreateSchema,
    ProductCreateSchema

)

from .client_schema import (
    ClientSchema,
    ClientListResponseSchema,
    ClientResponseSchema,
    ClientUpdateSchema,
    ClientCreateSchema,
    ClientBaseSchema,
    AddressSchema
)

from .review_schema import (
    ReviewBaseSchema,
    ReviewCreateSchema,
    ReviewSchema,
    ReviewUpdateSchema
)

from .base_schema import BaseSchema
from .product_schema import ProductSchema

__all__ = [
    'OrderDetailCreateSchema',
    'OrderCreateSchema', 
    'OrderUpdateSchema',
    'OrderSchema',
    'OrderDetailBaseSchema',
    'OrderCreateSchema',
    'OrderDetailCreateSchema',
    'OrderDetailUpdateSchema',
    
    'BillBase',
    'BillCreate',
    'BillResponse',
    
    'ClientSchema',
    'ClientListResponseSchema',
    'ClientResponseSchema',
    'ClientUpdateSchema',
    'ClientCreateSchema',
    'ClientBaseSchema',
    'AddressSchema',

    'ReviewBaseSchema',
    'ReviewCreateSchema',
    'ReviewSchema',
    'ReviewUpdateSchema',

    'ProductSchema',
    'ProductBaseSchema',
    'ProductCreateSchema',
]