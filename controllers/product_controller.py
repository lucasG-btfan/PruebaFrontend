from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List

# Mock data para desarrollo
mock_products = [
    {
        "id": 1,
        "name": "Laptop Gaming",
        "description": "Laptop para juegos de alta gama",
        "price": 1299.99,
        "stock": 15,
        "category_id": 1,
        "image_url": "https://via.placeholder.com/300"
    },
    {
        "id": 2,
        "name": "Mouse Inalámbrico",
        "description": "Mouse ergonómico inalámbrico",
        "price": 49.99,
        "stock": 50,
        "category_id": 2,
        "image_url": "https://via.placeholder.com/300"
    },
    {
        "id": 3,
        "name": "Teclado Mecánico",
        "description": "Teclado mecánico RGB",
        "price": 89.99,
        "stock": 30,
        "category_id": 2,
        "image_url": "https://via.placeholder.com/300"
    },
    {
        "id": 4,
        "name": "Monitor 27\"",
        "description": "Monitor 4K 27 pulgadas",
        "price": 399.99,
        "stock": 20,
        "category_id": 3,
        "image_url": "https://via.placeholder.com/300"
    }
]

# Router para productos
router = APIRouter(prefix="/api/v1/products", tags=["Products"])

@router.get("", response_model=List[dict])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None
):
    """Obtener lista de productos"""
    products = mock_products

    # Filtrar por búsqueda si se proporciona
    if search:
        search_lower = search.lower()
        products = [
            p for p in products
            if search_lower in p["name"].lower() or
               search_lower in p.get("description", "").lower()
        ]

    return {
        "products": products[skip:skip + limit],
        "total": len(products),
        "skip": skip,
        "limit": limit
    }

@router.get("/{product_id}", response_model=dict)
async def get_product(product_id: int):
    """Obtener un producto específico"""
    product = next((p for p in mock_products if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/search", response_model=dict)
async def search_products(q: str = Query(..., min_length=1)):
    """Buscar productos"""
    q_lower = q.lower()
    results = [
        p for p in mock_products
        if q_lower in p["name"].lower() or
           q_lower in p.get("description", "").lower()
    ]
    return {"products": results, "query": q, "count": len(results)}
