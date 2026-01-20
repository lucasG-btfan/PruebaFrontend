from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Dict, Any, List
from config.database import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/products")
async def create_product(
    product_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Crear un nuevo producto.
    """
    try:
        # Validar datos requeridos
        required_fields = ["name", "price", "stock"]
        for field in required_fields:
            if field not in product_data:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Campo requerido faltante: {field}"
                )
        
        # Preparar datos para la inserción
        insert_data = {
            "name": product_data["name"],
            "description": product_data.get("description", ""),
            "price": float(product_data["price"]),
            "stock": int(product_data["stock"]),
            "category_id": product_data.get("category_id"),
            "sku": product_data.get("sku", ""),
            "image_url": product_data.get("image_url", ""),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Ejecutar inserción usando SQL nativo
        query = text("""
            INSERT INTO products 
            (name, description, price, stock, category_id, sku, image_url, created_at, updated_at)
            VALUES 
            (:name, :description, :price, :stock, :category_id, :sku, :image_url, :created_at, :updated_at)
            RETURNING id_key
        """)
        
        result = db.execute(query, insert_data)
        product_id = result.scalar()
        db.commit()
        
        logger.info(f"✅ Producto creado ID: {product_id}")
        
        return {
            "success": True,
            "message": "Producto creado exitosamente",
            "product_id": product_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error creando producto: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error al crear producto: {str(e)}"
        )


@router.put("/products/{product_id}")
async def update_product(
    product_id: int,
    product_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Actualizar un producto existente.
    """
    try:
        logger.info(f"📥 PUT /products/{product_id} - Datos recibidos: {product_data}")
        
        check_query = text("SELECT id_key FROM products WHERE id_key = :product_id")
        check_result = db.execute(check_query, {"product_id": product_id})
        if not check_result.fetchone():
            logger.error(f"❌ Producto {product_id} no encontrado")
            raise HTTPException(
                status_code=404,
                detail=f"Producto con ID {product_id} no encontrado"
            )
        
        update_fields = []
        update_values = {"product_id": product_id}
        
        if "name" in product_data:
            update_fields.append("name = :name")
            update_values["name"] = product_data["name"]
        
        if "description" in product_data:
            update_fields.append("description = :description")
            update_values["description"] = product_data["description"]
        
        if "price" in product_data:
            update_fields.append("price = :price")
            update_values["price"] = float(product_data["price"])
        
        if "stock" in product_data:
            update_fields.append("stock = :stock")
            update_values["stock"] = int(product_data["stock"])
        
        if "category_id" in product_data:
            update_fields.append("category_id = :category_id")
            update_values["category_id"] = product_data["category_id"]
        
        if "sku" in product_data:
            update_fields.append("sku = :sku")
            update_values["sku"] = product_data["sku"]
        
        if "image_url" in product_data:
            update_fields.append("image_url = :image_url")
            update_values["image_url"] = product_data["image_url"]
        
        update_fields.append("updated_at = :updated_at")
        update_values["updated_at"] = datetime.utcnow()
        
        if not update_fields:
            logger.error("❌ No se proporcionaron datos para actualizar")
            raise HTTPException(
                status_code=400,
                detail="No se proporcionaron datos para actualizar"
            )
        
        update_query = text(f"""
            UPDATE products 
            SET {', '.join(update_fields)}
            WHERE id_key = :product_id
        """)
        
        logger.info(f"📝 Query de actualización: {update_query}")
        logger.info(f"📝 Valores: {update_values}")
        
        result = db.execute(update_query, update_values)
        db.commit()
        
        logger.info(f"✅ Producto actualizado ID: {product_id}")
        
        get_query = text("""
            SELECT * FROM products WHERE id_key = :product_id
        """)
        updated_product = db.execute(get_query, {"product_id": product_id}).fetchone()
        
        product_dict = {}
        if updated_product:
            columns = updated_product._mapping.keys()
            for column in columns:
                product_dict[column] = getattr(updated_product, column)
        
        return {
            "success": True,
            "message": "Producto actualizado exitosamente",
            "product_id": product_id,
            "data": product_dict
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error actualizando producto: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error al actualizar producto: {str(e)}"
        )


@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Eliminar un producto (borrado lógico o físico según tu lógica de negocio).
    """
    try:
        # Verificar que el producto existe
        check_query = text("SELECT id_key FROM products WHERE id_key = :product_id")
        check_result = db.execute(check_query, {"product_id": product_id})
        if not check_result.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Producto con ID {product_id} no encontrado"
            )
        
        delete_query = text("DELETE FROM products WHERE id_key = :product_id")
        
        result = db.execute(delete_query, {"product_id": product_id})
        db.commit()
        
        logger.info(f"✅ Producto eliminado ID: {product_id}")
        
        return {
            "success": True,
            "message": "Producto eliminado exitosamente",
            "product_id": product_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error eliminando producto: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error al eliminar producto: {str(e)}"
        )

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