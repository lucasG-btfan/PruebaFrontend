# schemas/__init__.py
"""
Pydantic schemas for request/response validation.
"""

# Importar la base
from schemas.base_schema import BaseSchema

# Listar todos los esquemas disponibles
__all__ = [
    'BaseSchema',
    'ClientSchema',
    'ClientCreateSchema',
    'ClientUpdateSchema',
    'ClientResponseSchema',
    'ProductSchema',
    'CategorySchema',
    'AddressSchema',
    'OrderSchema',
    'OrderDetailSchema',
    'BillSchema',
    'ReviewSchema'
]

print("📄 Initializing schemas package...")

# NOTA: Los esquemas específicos se importarán cuando sean necesarios
# para evitar problemas de importación circular