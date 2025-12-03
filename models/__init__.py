# models/__init__.py
"""
Initialize models package and ensure all models are imported.
This helps SQLAlchemy discover all models.
"""

# Importar la base compartida
from models.base_model import base as Base

# Lista de todos los modelos para facilitar importaciones
__all__ = [
    'Base',
    'ClientModel',
    'ProductModel',
    'CategoryModel',
    'AddressModel',
    'OrderModel',
    'OrderDetailModel',
    'BillModel',
    'ReviewModel'
]

print("📦 Initializing models package...")

# NOTA: No importamos los modelos aquí directamente
# Los importaremos solo cuando sea necesario para evitar imports circulares