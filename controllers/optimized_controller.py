from fastapi import APIRouter

router = APIRouter()

@router.get("/optimized")
async def get_optimized_data():
    """Endpoint optimizado que devuelve datos consolidados"""
    return {
        "message": "Optimized endpoint",
        "endpoints": {
            "clients": "/api/v1/clients",
            "products": "/api/v1/products", 
            "orders": "/api/v1/orders"
        },
        "status": "operational"
    }