"""
Initialize models package and ensure all models are imported.
This helps SQLAlchemy discover all models.
"""
import logging

logger = logging.getLogger(__name__)

# Importar la base compartida
from .base_model import Base, BaseModel

# Importar todos los modelos para que se registren con Base
try:
    from .client import ClientModel
    from .bill import BillModel
    from .order import OrderModel
    from .order_detail import OrderDetailModel
    from .product import ProductModel
    from .category import CategoryModel
    from .address import AddressModel
    from .review import ReviewModel
    
    logger.info("📦 All models imported successfully")
    
except ImportError as e:
    logger.error(f"❌ Failed to import models: {e}")
    raise

# Lista de todos los modelos
__all__ = [
    'Base',
    'BaseModel',
    'ClientModel',
    'BillModel',  
    'OrderModel',
    'OrderDetailModel',
    'ProductModel',
    'CategoryModel',
    'AddressModel',
    'ReviewModel'
]