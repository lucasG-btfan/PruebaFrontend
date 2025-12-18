from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from config.database import get_db

router = APIRouter(prefix="/api/v1", tags=["products"])

@router.get("/products", response_model=Dict[str, Any])
async def get_products(
    skip: int = Query(0, ge=0, description="Número de productos a saltar"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de productos a devolver"),
    search: Optional[str] = Query(None, description="Término de búsqueda en nombre o descripción"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Obtener lista de productos con paginación y opción de búsqueda.
    Versión temporal evitando relaciones problemáticas.
    """
    try:
        query = """
            SELECT
                id_key, name, description, price,
                stock, category_id, sku, image_url,
                created_at, updated_at
            FROM products
            WHERE stock > 0
            ORDER BY name
            LIMIT :limit OFFSET :skip
        """
        if search:
            search_term = f"%{search.lower()}%"
            query = """
                SELECT
                    id_key, name, description, price,
                    stock, category_id, sku, image_url,
                    created_at, updated_at
                FROM products
                WHERE stock > 0 AND
                (LOWER(name) LIKE :search OR LOWER(description) LIKE :search)
                ORDER BY name
                LIMIT :limit OFFSET :skip
            """
            result = db.execute(text(query), {"search": search_term, "limit": limit, "skip": skip})
        else:
            result = db.execute(text(query), {"limit": limit, "skip": skip})

        products = []
        for row in result:
            product_dict = dict(row)
            if product_dict.get('price'):
                product_dict['price'] = float(product_dict['price'])
            products.append(product_dict)

        return {
            "success": True,
            "data": products,
            "count": len(products),
            "skip": skip,
            "limit": limit
        }

    except Exception as e:
        # Log del error para debugging
        print(f"Error en get_products: {str(e)}")
        return {
            "success": False,
            "data": [],
            "error": str(e),
            "skip": skip,
            "limit": limit
        }

@router.get("/products/search", response_model=Dict[str, Any])
async def search_products(
    q: str = Query(..., min_length=1, description="Término de búsqueda obligatorio"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Buscar productos por término de búsqueda en nombre o descripción.
    """
    try:
        search_term = f"%{q.lower()}%"
        query = """
            SELECT
                id_key, name, description, price,
                stock, category_id, sku, image_url,
                created_at, updated_at
            FROM products
            WHERE stock > 0 AND
            (LOWER(name) LIKE :search OR LOWER(description) LIKE :search)
            ORDER BY name
            LIMIT 100
        """
        result = db.execute(text(query), {"search": search_term})

        products = []
        for row in result:
            product_dict = dict(row)
            if product_dict.get('price'):
                product_dict['price'] = float(product_dict['price'])
            products.append(product_dict)

        return {
            "success": True,
            "data": products,
            "query": q,
            "count": len(products)
        }

    except Exception as e:
        print(f"Error en search_products: {str(e)}")
        return {
            "success": False,
            "data": [],
            "error": str(e),
            "query": q
        }
