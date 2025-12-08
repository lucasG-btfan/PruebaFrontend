from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any

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

router = APIRouter(
    prefix="/api/v1/products",
    tags=["Products"],
    responses={404: {"description": "Product not found"}}
)

@router.get("", response_model=Dict[str, Any])
async def get_products(
    skip: int = Query(0, ge=0, description="Número de productos a saltar"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de productos a devolver"),
    search: Optional[str] = Query(None, description="Término de búsqueda en nombre o descripción")
) -> Dict[str, Any]:
    """
    Obtener lista de productos con paginación y opción de búsqueda.
    """
    filtered_products = mock_products
    if search:
        search_lower = search.lower()
        filtered_products = [
            product for product in filtered_products
            if (search_lower in product["name"].lower() or
                search_lower in product.get("description", "").lower())
        ]

    paginated_products = filtered_products[skip:skip + limit]

    return {
        "products": paginated_products,
        "total": len(filtered_products),
        "skip": skip,
        "limit": limit
    }

@router.get("/search", response_model=Dict[str, Any])
async def search_products(
    q: str = Query(..., min_length=1, description="Término de búsqueda obligatorio")
) -> Dict[str, Any]:
    """
    Buscar productos por término de búsqueda en nombre o descripción.
    """
    q_lower = q.lower()
    results = [
        product for product in mock_products
        if (q_lower in product["name"].lower() or
            q_lower in product.get("description", "").lower())
    ]
    return {
        "products": results,
        "query": q,
        "count": len(results)
    }

@router.get("/{product_id}", response_model=Dict[str, Any])
async def get_product(product_id: int) -> Dict[str, Any]:
    """
    Obtener un producto específico por su ID.
    """
    product = next((p for p in mock_products if p["id"] == product_id), None)
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Product with ID {product_id} not found"
        )
    return product