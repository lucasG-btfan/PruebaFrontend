"""
Initialize models package and ensure all models are imported.
This helps SQLAlchemy discover all models.
"""
import logging

logger = logging.getLogger(__name__)

# Importar la base compartida
from .base_model import Base, BaseModel


try:
    # Importar modelos en orden jerárquico
    
    from .category import CategoryModel
    from .client import ClientModel
    from .product import ProductModel
    from .order import OrderModel
    from .order_detail import OrderDetailModel
    from .bill import BillModel
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
    'CategoryModel',
    'ClientModel',
    'ProductModel',
    'OrderModel',
    'OrderDetailModel',
    'BillModel',
    'AddressModel',
    'ReviewModel'
]