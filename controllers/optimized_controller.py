# controllers/optimized_controller.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/optimized")
async def get_optimized():
    """Endpoint optimizado para datos consolidados"""
    return {
        "message": "Optimized API endpoint",
        "version": "1.0",
        "endpoints": {
            "health": "/health",
            "clients": "/api/v1/clients",
            "products": "/api/v1/products",
            "orders": "/api/v1/orders",
            "bills": "/api/v1/bills"
        }
    }