"""
Initialize models package and ensure all models are imported.
This helps SQLAlchemy discover all models.
"""
# Importar la base compartida y BaseModel
from .base_model import Base, BaseModel

# Importar todos los modelos para que se registren con Base
from .client import ClientModel
from .bill import BillModel
from .order import OrderModel
from .order_detail import OrderDetailModel
from .product import ProductModel
from .category import CategoryModel
from .address import AddressModel
from .review import ReviewModel

# Lista de todos los modelos para facilitar importaciones
__all__ = [
    'Base',
    'Base',
    'Client',
    'BillModel',
    'OrderModel',
    'OrderDetailModel',
    'ProductModel',
    'CategoryModel',
    'AddressModel',
    'ReviewModel'
]

print("📦 Initializing models package...")
