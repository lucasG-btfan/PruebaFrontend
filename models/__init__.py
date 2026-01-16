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

    logger.info("📦 Todos los modelos importados correctamente")

    # Verificar que todos los modelos estén registrados
    if hasattr(Base, 'registry') and hasattr(Base.registry, '_class_registry'):
        registered_classes = list(Base.registry._class_registry.keys())
        logger.info(f"📦 Clases registradas con Base: {registered_classes}")

        if 'ReviewModel' not in registered_classes:
            logger.error("❌ ReviewModel NO está registrado en Base.registry")
        else:
            logger.info("✅ ReviewModel registrado correctamente en Base.registry")

except ImportError as e:
    logger.error(f"❌ Falló la importación de modelos: {e}")
    raise
