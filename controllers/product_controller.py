from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from config.database import get_db
from schemas.product_schema import ProductCreateSchema, ProductUpdateSchema, ProductSchema
from services.product_service import ProductService

router = APIRouter(
    tags=["Products"],
    responses={404: {"description": "Product not found"}}
)

@router.get("", response_model=Dict[str, Any])
async def get_products(
    skip: int = Query(0, ge=0, description="Número de productos a saltar"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de productos a devolver"),
    search: Optional[str] = Query(None, description="Término de búsqueda en nombre o descripción"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Obtener lista de productos con paginación y opción de búsqueda.
    """
    try:
        product_service = ProductService(db)
        products = product_service.get_all(skip, limit)
        
        filtered_products = products
        if search:
            search_lower = search.lower()
            filtered_products = [
                product for product in products
                if (search_lower in product.name.lower() or
                    search_lower in (product.description or "").lower())
            ]
        
        paginated_products = filtered_products[skip:skip + limit]
        
        return {
            "products": paginated_products,
            "total": len(filtered_products),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener productos: {str(e)}"
        )

@router.post("", response_model=Dict[str, Any], status_code=201)
async def create_product(
    product_data: ProductCreateSchema,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Crear un nuevo producto.
    
    - **product_data**: Datos del producto a crear.
    """
    try:
        product_service = ProductService(db)
        
        product = product_service.save(product_data)
        
        return {
            "message": "Product created successfully",
            "product_id": product.id_key,
            "product": product
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error en los datos: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {str(e)}"
        )

@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
) -> ProductSchema:
    """
    Obtener un producto específico por su ID.
    """
    try:
        product_service = ProductService(db)
        product = product_service.get_one(product_id)
        
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product with ID {product_id} not found"
            )
            
        return product
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener el producto: {str(e)}"
        )

@router.put("/{product_id}", response_model=Dict[str, Any])
async def update_product(
    product_id: int,
    product_data: ProductUpdateSchema,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Actualizar un producto existente.
    """
    try:
        product_service = ProductService(db)
        existing_product = product_service.get_one(product_id)
        if not existing_product:
            raise HTTPException(
                status_code=404,
                detail=f"Product with ID {product_id} not found"
            )
        
        update_dict = product_data.dict(exclude_unset=True)
        
        updated_schema = ProductSchema(
            **existing_product.dict(),
            **update_dict
        )
        
        product = product_service.update(product_id, updated_schema)
        
        return {
            "message": "Product updated successfully",
            "product": product
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar el producto: {str(e)}"
        )

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Eliminar un producto.
    """
    try:
        product_service = ProductService(db)
        
        existing_product = product_service.get_one(product_id)
        if not existing_product:
            raise HTTPException(
                status_code=404,
                detail=f"Product with ID {product_id} not found"
            )
        product_service.delete(product_id)
        
        return {
            "message": f"Product with ID {product_id} deleted successfully",
            "deleted_id": product_id
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar el producto: {str(e)}"
        )

@router.get("/search", response_model=Dict[str, Any])
async def search_products(
    q: str = Query(..., min_length=1, description="Término de búsqueda obligatorio"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Buscar productos por término de búsqueda en nombre o descripción.
    """
    try:
        product_service = ProductService(db)
        
        all_products = product_service.get_all(skip=0, limit=1000) 
        
        q_lower = q.lower()
        results = [
            product for product in all_products
            if (q_lower in product.name.lower() or
                q_lower in (product.description or "").lower())
        ]
        
        return {
            "products": results,
            "query": q,
            "count": len(results)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en la búsqueda: {str(e)}"
        )