from __future__ import annotations
import logging
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from schemas.product_schema import ProductSchema
    from schemas.client_schema import ClientSchema
    from schemas.order_schema import OrderSchema
    from schemas.order_detail_schema import OrderDetailSchema
    from schemas.bill_schema import BillResponse


def rebuild_models():
    """
    Reconstruir modelos Pydantic para resolver referencias circulares.
    IMPORTANTE: Importar TODOS los schemas antes de reconstruir.
    """
    try:
        logger.info("Iniciando reconstrucción de modelos...")
        
        # Importar todos los schemas necesarios
        from schemas.product_schema import ProductSchema, ProductBaseSchema
        from schemas.client_schema import ClientSchema, ClientResponseSchema
        from schemas.order_schema import OrderSchema, OrderCreateSchema, OrderUpdateSchema
        from schemas.order_detail_schema import (
            OrderDetailSchema, 
            OrderDetailBase, 
            OrderDetailBaseSchema
        )
        from schemas.bill_schema import BillResponse, BillBase
        
        logger.info("✓ Todos los schemas importados")
        
        # Reconstruir en orden de dependencias
        models_to_rebuild = [
            ("ProductSchema", ProductSchema),
            ("ProductBaseSchema", ProductBaseSchema),
            ("ClientSchema", ClientSchema),
            ("ClientResponseSchema", ClientResponseSchema),
            ("OrderSchema", OrderSchema),
            ("OrderCreateSchema", OrderCreateSchema),
            ("OrderUpdateSchema", OrderUpdateSchema),
            ("OrderDetailSchema", OrderDetailSchema),
            ("OrderDetailBase", OrderDetailBase),
            ("OrderDetailBaseSchema", OrderDetailBaseSchema),
            ("BillBase", BillBase),
            ("BillResponse", BillResponse),
        ]
        
        for name, model in models_to_rebuild:
            try:
                if hasattr(model, 'model_rebuild'):
                    model.model_rebuild()
                    logger.info(f"  ✓ {name} reconstruido")
                else:
                    logger.warning(f"  ⚠ {name}: no tiene model_rebuild (Pydantic v1?)")
            except Exception as e:
                logger.error(f"  ✗ Error reconstruyendo {name}: {e}")
        
        logger.info("✓ Reconstrucción de modelos completada")
        return True
        
    except ImportError as e:
        logger.error(f"✗ Error importando schemas: {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"✗ Error general en rebuild_models: {e}", exc_info=True)
        return False


def verify_schemas():
    """
    Verificar que todos los schemas se puedan importar correctamente.
    """
    try:
        logger.info("Verificando schemas...")
        
        # Importar sin dependencias circulares
        from schemas.product_schema import ProductSchema
        from schemas.client_schema import ClientSchema
        from schemas.order_schema import OrderSchema
        from schemas.order_detail_schema import OrderDetailSchema
        from schemas.bill_schema import BillResponse
        
        logger.info("✓ Verificación exitosa")
        logger.info(f"  - ProductSchema: {ProductSchema}")
        logger.info(f"  - ClientSchema: {ClientSchema}")
        logger.info(f"  - OrderSchema: {OrderSchema}")
        logger.info(f"  - OrderDetailSchema: {OrderDetailSchema}")
        logger.info(f"  - BillResponse: {BillResponse}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Error verificando schemas: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("\n" + "="*60)
    print("VERIFICACIÓN Y RECONSTRUCCIÓN DE SCHEMAS")
    print("="*60 + "\n")
    
    # Primero verificar
    if verify_schemas():
        print("\n" + "-"*60)
        print("RECONSTRUYENDO MODELOS...")
        print("-"*60)
        rebuild_models()
    
    print("\n" + "="*60)