from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import text
from config.database import get_db

router = APIRouter() 

@router.get("/products", response_model=Dict[str, Any])
async def get_products(
    skip: int = Query(0, ge=0, description="Número de productos a saltar"),
    limit: int = Query(12, ge=1, le=100, description="Número máximo de productos a devolver"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Obtener todos los productos con paginación.
    """
    try:
        query = text("""
            SELECT
                id_key, name, description, price,
                stock, category_id, sku, image_url,
                created_at, updated_at
            FROM products
            WHERE stock > 0
            ORDER BY name
            OFFSET :skip LIMIT :limit
        """)

        result = db.execute(query, {"skip": skip, "limit": limit})
        products = [dict(row) for row in result]

        # Obtener conteo total
        count_query = text("SELECT COUNT(*) FROM products WHERE stock > 0")
        total_result = db.execute(count_query)
        total = total_result.scalar()

        # Convertir Decimal a float para JSON
        for product in products:
            if product.get('price'):
                product['price'] = float(product['price'])

        return {
            "success": True,
            "products": products,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    except Exception as e:
        print(f"Error en get_products: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener productos: {str(e)}"
        )

@router.get("/products/search", response_model=Dict[str, Any])
async def search_products(
    q: str = Query("", min_length=0, description="Término de búsqueda"),
    skip: int = Query(0, ge=0, description="Número de productos a saltar"),
    limit: int = Query(12, ge=1, le=100, description="Número máximo de productos a devolver"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Buscar productos por nombre o descripción.
    """
    try:
        if not q:
            return await get_products(skip=skip, limit=limit, db=db)

        query = text("""
            SELECT
                id_key, name, description, price,
                stock, category_id, sku, image_url,
                created_at, updated_at
            FROM products
            WHERE (LOWER(name) LIKE LOWER(:search)
                   OR LOWER(description) LIKE LOWER(:search))
              AND stock > 0
            ORDER BY name
            OFFSET :skip LIMIT :limit
        """)

        result = db.execute(query, {
            "search": f"%{q}%",
            "skip": skip,
            "limit": limit
        })
        products = [dict(row) for row in result]

        # Obtener conteo
        count_query = text("""
            SELECT COUNT(*)
            FROM products
            WHERE (LOWER(name) LIKE LOWER(:search)
                   OR LOWER(description) LIKE LOWER(:search))
              AND stock > 0
        """)
        total_result = db.execute(count_query, {"search": f"%{q}%"})
        total = total_result.scalar()

        # Convertir Decimal a float
        for product in products:
            if product.get('price'):
                product['price'] = float(product['price'])

        return {
            "success": True,
            "products": products,
            "query": q,
            "count": total,
            "skip": skip,
            "limit": limit
        }

    except Exception as e:
        print(f"Error en search_products: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al buscar productos: {str(e)}"
        )

@router.get("/products/{product_id}", response_model=Dict[str, Any])
async def get_product_by_id(
    product_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Obtener un producto por su ID.
    """
    try:
        query = text("""
            SELECT
                id_key, name, description, price,
                stock, category_id, sku, image_url,
                created_at, updated_at
            FROM products
            WHERE id_key = :product_id
        """)

        result = db.execute(query, {"product_id": product_id})
        product_row = result.fetchone()

        if not product_row:
            raise HTTPException(
                status_code=404,
                detail=f"Producto con ID {product_id} no encontrado"
            )

        product = dict(product_row)

        # Convertir Decimal a float
        if product.get('price'):
            product['price'] = float(product['price'])

        return {
            "success": True,
            "data": product
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en get_product_by_id: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener producto: {str(e)}"
        )
