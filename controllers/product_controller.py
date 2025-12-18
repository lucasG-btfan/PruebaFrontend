from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, List
from config.database import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/products")
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(12, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Obtener todos los productos con paginación.
    """
    try:
        # Query para obtener productos
        query = text("""
            SELECT 
                id_key, 
                name, 
                description, 
                price::float, 
                stock, 
                category_id, 
                COALESCE(sku, '') as sku, 
                COALESCE(image_url, '') as image_url,
                created_at, 
                updated_at
            FROM products 
            WHERE stock > 0
            ORDER BY id_key
            OFFSET :skip LIMIT :limit
        """)
        
        # Ejecutar consulta
        result = db.execute(query, {"skip": skip, "limit": limit})
        
        # Procesar resultados CORRECTAMENTE
        products = []
        columns = result.keys()  # Obtener nombres de columnas
        
        for row in result:
            # Crear diccionario manualmente
            product_dict = {}
            for i, column in enumerate(columns):
                value = row[i]
                # Convertir Decimal a float si es necesario
                if column == 'price' and value is not None:
                    try:
                        value = float(value)
                    except:
                        value = 0.0
                product_dict[column] = value
            products.append(product_dict)
        
        # Query para contar total
        count_query = text("SELECT COUNT(*) as total FROM products WHERE stock > 0")
        count_result = db.execute(count_query)
        total = count_result.scalar()
        
        logger.info(f"✅ Productos obtenidos: {len(products)} de {total}")
        
        return {
            "success": True,
            "products": products,
            "total": total,
            "skip": skip,
            "limit": limit,
            "count": len(products)
        }
        
    except Exception as e:
        logger.error(f"❌ Error en get_products: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error al obtener productos: {str(e)}"
        )

@router.get("/products/search")
async def search_products(
    q: str = Query("", min_length=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(12, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Buscar productos por nombre o descripción.
    """
    try:
        search_term = f"%{q}%" if q else "%%"
        
        query = text("""
            SELECT 
                id_key, 
                name, 
                description, 
                price::float, 
                stock, 
                category_id, 
                COALESCE(sku, '') as sku, 
                COALESCE(image_url, '') as image_url,
                created_at, 
                updated_at
            FROM products 
            WHERE (LOWER(name) LIKE LOWER(:search) 
                   OR LOWER(description) LIKE LOWER(:search))
              AND stock > 0
            ORDER BY name
            OFFSET :skip LIMIT :limit
        """)
        
        result = db.execute(query, {
            "search": search_term,
            "skip": skip, 
            "limit": limit
        })
        
        products = []
        columns = result.keys()
        
        for row in result:
            product_dict = {}
            for i, column in enumerate(columns):
                value = row[i]
                if column == 'price' and value is not None:
                    try:
                        value = float(value)
                    except:
                        value = 0.0
                product_dict[column] = value
            products.append(product_dict)
        
        # Contar resultados de búsqueda
        count_query = text("""
            SELECT COUNT(*) as count 
            FROM products 
            WHERE (LOWER(name) LIKE LOWER(:search) 
                   OR LOWER(description) LIKE LOWER(:search))
              AND stock > 0
        """)
        count_result = db.execute(count_query, {"search": search_term})
        total_count = count_result.scalar()
        
        return {
            "success": True,
            "products": products,
            "query": q,
            "count": total_count,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"❌ Error en search_products: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error al buscar productos: {str(e)}"
        )

@router.get("/products/{product_id}")
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
                id_key, 
                name, 
                description, 
                price::float, 
                stock, 
                category_id, 
                COALESCE(sku, '') as sku, 
                COALESCE(image_url, '') as image_url,
                created_at, 
                updated_at
            FROM products 
            WHERE id_key = :product_id
        """)
        
        result = db.execute(query, {"product_id": product_id})
        
        # Usar fetchone para obtener un solo resultado
        row = result.fetchone()
        
        if not row:
            raise HTTPException(
                status_code=404,
                detail=f"Producto con ID {product_id} no encontrado"
            )
        
        # Convertir a diccionario
        product = {}
        columns = result.keys()
        for i, column in enumerate(columns):
            value = row[i]
            if column == 'price' and value is not None:
                try:
                    value = float(value)
                except:
                    value = 0.0
            product[column] = value
        
        return {
            "success": True,
            "data": product
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en get_product_by_id: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener producto: {str(e)}"
        )

# Endpoint de prueba
@router.get("/test")
async def test_endpoint():
    return {
        "success": True,
        "message": "Product router working",
        "status": "ok"
    }