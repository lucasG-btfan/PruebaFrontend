"""
Pydantic schemas for request/response validation.
"""
# Importar la base
from .base_schema import BaseSchema

# Importar todos los esquemas
from .client_schema import (
    ClientSchema, 
    ClientCreateSchema, 
    ClientUpdateSchema, 
    ClientResponseSchema, 
    ClientListResponseSchema
)
from .bill_schema import BillSchema
from .order_schema import OrderSchema
from .order_detail_schema import OrderDetailSchema
from .product_schema import ProductSchema
from .category_schema import CategorySchema
from .address_schema import AddressSchema
from .review_schema import ReviewSchema

# Listar todos los esquemas disponibles
__all__ = [
    'BaseSchema',
    'ClientSchema',
    'ClientCreateSchema',
    'ClientUpdateSchema',
    'ClientResponseSchema',
    'ClientListResponseSchema',
    'BillSchema',
    'OrderSchema',
    'OrderDetailSchema',
    'ProductSchema',
    'CategorySchema',
    'AddressSchema',
    'ReviewSchema'
]

print("📄 Initializing schemas package...")
