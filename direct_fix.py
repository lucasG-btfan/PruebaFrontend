# direct_fix.py
"""
Solución directa: Asumir que todas las clases son sin 'Model'.
"""
import os

print("🔧 APLICANDO SOLUCIÓN DIRECTA")
print("=" * 50)

# 1. Asegurar que models/__init__.py importe Client (no ClientModel)
init_content = '''"""
Initialize models package and ensure all models are imported.
This helps SQLAlchemy discover all models.
"""
from .base_model import Base, BaseModel

# Importar todos los modelos para que se registren con Base
from .client import ClientModel
from .bill import Bill
from .order import Order
from .order_detail import OrderDetail
from .product import Product
from .category import Category
from .address import Address
from .review import Review

# Lista de todos los modelos para facilitar importaciones
__all__ = [
    'Base',
    'BaseModel',
    'ClientModel',
    'Bill',
    'Order',
    'OrderDetail',
    'Product',
    'Category',
    'Address',
    'Review'
]

print("📦 Models package initialized")
'''

with open("models/__init__.py", "w", encoding="utf-8") as f:
    f.write(init_content)
print("✅ models/__init__.py actualizado")

# 2. Asegurar que schemas/__init__.py tenga ClientSchema
schemas_content = '''"""
Pydantic schemas for request/response validation.
"""
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

print("📄 Schemas package initialized")
'''

with open("schemas/__init__.py", "w", encoding="utf-8") as f:
    f.write(schemas_content)
print("✅ schemas/__init__.py actualizado")

# 3. Verificar client_schema.py tiene ClientSchema
try:
    with open("schemas/client_schema.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    if "ClientSchema = ClientResponseSchema" not in content:
        # Añadir al final del archivo
        with open("schemas/client_schema.py", "a", encoding="utf-8") as f:
            f.write("\n\n# Alias para compatibilidad\nClientSchema = ClientResponseSchema\n")
        print("✅ ClientSchema alias añadido a client_schema.py")
    else:
        print("✅ ClientSchema ya existe en client_schema.py")
        
except Exception as e:
    print(f"⚠️ Error verificando client_schema.py: {e}")

print("\n" + "=" * 50)
print("🎯 SOLUCIÓN APLICADA")
print("\nAhora prueba con:")
print("python -c \"from models import Client; print('✅ Client importado')\"")