# controllers/product_controller.py
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from controllers.base_controller_impl import BaseControllerImpl
from schemas.product_schema import ProductSchema, ProductCreate, ProductUpdate, ProductResponse
from services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])

class ProductController(BaseControllerImpl):
    """Controller for Product entity with CRUD operations."""

    def __init__(self):
        super().__init__(
            schema=ProductSchema,
            service_factory=lambda db: ProductService(db),
            tags=["Products"]
        )

    @router.get("", response_model=List[ProductResponse])
    async def get_products(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, le=500),
        search: Optional[str] = None,
        service: ProductService = Depends(lambda: ProductService())
    ):
        """Get all products with optional search."""
        try:
            products = await service.get_all(skip=skip, limit=limit, search=search)
            return products
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("", response_model=ProductResponse, status_code=201)
    async def create_product(
        product_data: ProductCreate,
        service: ProductService = Depends(lambda: ProductService())
    ):
        """Create a new product."""
        try:
            product = await service.create(product_data)
            return product
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.get("/{product_id}", response_model=ProductResponse)
    async def get_product(
        product_id: int,
        service: ProductService = Depends(lambda: ProductService())
    ):
        """Get a product by ID."""
        try:
            product = await service.get_by_id(product_id)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            return product
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.put("/{product_id}", response_model=ProductResponse)
    async def update_product(
        product_id: int,
        product_data: ProductUpdate,
        service: ProductService = Depends(lambda: ProductService())
    ):
        """Update a product by ID."""
        try:
            product = await service.update(product_id, product_data)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            return product
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.delete("/{product_id}", status_code=204)
    async def delete_product(
        product_id: int,
        service: ProductService = Depends(lambda: ProductService())
    ):
        """Delete a product by ID."""
        try:
            await service.delete(product_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# Instancia del controlador para registrar rutas
product_controller = ProductController()
