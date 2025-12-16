from __future__ import annotations

def rebuild_models():
    """Reconstruir modelos para resolver referencias circulares"""
    try:
        from schemas.base_schema import BaseModel
        from schemas.order_schema import OrderSchema
        from schemas.order_detail_schema import OrderDetailSchema
        from schemas.bill_schema import BillResponse
        from schemas.product_schema import ProductBaseSchema
        
        # Reconstruir en orden
        BaseModel.model_rebuild()
        ProductBaseSchema.model_rebuild()
        OrderSchema.model_rebuild()
        OrderDetailSchema.model_rebuild()
        BillResponse.model_rebuild()
        
        print("✓ Modelos reconstruidos exitosamente")
    except Exception as e:
        print(f"⚠ Error reconstruyendo modelos: {e}")