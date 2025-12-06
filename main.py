"""
Main FastAPI application - Simple version for production.
Uses centralized constants from config.constants.py.
"""
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Importar constantes centralizadas desde config.constants
from config.constants import (
    APP_NAME,
    APP_DESCRIPTION,
    APP_VERSION,
    HOST,
    PORT,
    ENABLE_DOCS,
    ALLOWED_ORIGINS,
    LOG_LEVEL,
    LOG_FILE,
    ERROR_LOG_FILE
)

# Importar TODOS los routers necesarios
from controllers.health_check import router as health_router
from controllers.product_controller import router as product_router
from controllers.client_controller import router as client_router
from controllers.order_controller import router as order_router
from controllers.order_detail_controller import router as order_detail_router
from controllers.category_controller import router as category_router
from controllers.bill_controller import router as bill_router
from controllers.review_controller import router as review_router
from controllers.address_controller import router as address_router
from controllers.test_controller import router as test_router

# Configurar logging CORREGIDO
app_handler = logging.FileHandler(LOG_FILE)
error_handler = logging.FileHandler(ERROR_LOG_FILE)
console_handler = logging.StreamHandler()

# Configurar niveles
app_handler.setLevel(LOG_LEVEL)
error_handler.setLevel(logging.ERROR)  # Solo errores para este archivo
console_handler.setLevel(LOG_LEVEL)

# Configurar el formato
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
app_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Configurar el logger raíz
logging.basicConfig(
    level=LOG_LEVEL,
    handlers=[app_handler, error_handler, console_handler]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager."""
    logger.info("🚀 Starting E-commerce API...")
    # Intentar conectar a base de datos
    try:
        from config.database_render import check_connection, create_tables
        if check_connection():
            logger.info("✅ Database connected")
            create_tables()
            logger.info("✅ Tables created/verified")
    except Exception as e:
        logger.warning(f"⚠️ Database setup skipped: {e}")
    yield
    logger.info("👋 Shutting down...")

# Crear aplicación FastAPI
app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url="/docs" if ENABLE_DOCS else None,
    redoc_url="/redoc" if ENABLE_DOCS else None,
    openapi_url="/openapi.json" if ENABLE_DOCS else None,
    lifespan=lifespan
)

# Incluir TODOS los routers con sus prefijos
app.include_router(health_router, tags=["health"])
app.include_router(product_router, prefix="/api/v1", tags=["products"])
app.include_router(client_router, prefix="/api/v1", tags=["clients"])
app.include_router(order_router, prefix="/api/v1", tags=["orders"])
app.include_router(order_detail_router, prefix="/api/v1", tags=["order-details"])
app.include_router(category_router, prefix="/api/v1", tags=["categories"])
app.include_router(bill_router, prefix="/api/v1", tags=["bills"])
app.include_router(review_router, prefix="/api/v1", tags=["reviews"])
app.include_router(address_router, prefix="/api/v1", tags=["addresses"])
app.include_router(test_router, prefix="/api/v1", tags=["test"])

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "E-commerce REST API",
        "version": APP_VERSION,
        "docs": "/docs",
        "health": "/health_check"
    }

# Health check endpoint (mantener por compatibilidad)
@app.get("/health_check")
async def health_check():
    return {"status": "healthy", "timestamp": "now"}

@app.get("/api/v1/products")
async def get_products(skip: int = 0, limit: int = 100):
    """Get all products (mock data for now)."""
    products = [
        {
            "id": 1,
            "name": "Laptop Gaming Pro",
            "price": 1299.99,
            "description": "High-performance gaming laptop with RTX 4070",
            "image_url": "https://picsum.photos/300/200?random=1",
            "stock": 15,
            "category": "Electronics"
        },
        {
            "id": 2,
            "name": "Wireless Mouse",
            "price": 49.99,
            "description": "Ergonomic wireless mouse with RGB lighting",
            "image_url": "https://picsum.photos/300/200?random=2",
            "stock": 42,
            "category": "Accessories"
        },
        {
            "id": 3,
            "name": "Mechanical Keyboard",
            "price": 89.99,
            "description": "RGB mechanical keyboard with blue switches",
            "image_url": "https://picsum.photos/300/200?random=3",
            "stock": 23,
            "category": "Accessories"
        },
        {
            "id": 4,
            "name": "4K Monitor",
            "price": 399.99,
            "description": "27-inch 4K UHD monitor with HDR",
            "image_url": "https://picsum.photos/300/200?random=4",
            "stock": 8,
            "category": "Electronics"
        },
        {
            "id": 5,
            "name": "Gaming Headset",
            "price": 79.99,
            "description": "7.1 Surround Sound gaming headset",
            "image_url": "https://picsum.photos/300/200?random=5",
            "stock": 32,
            "category": "Accessories"
        }
    ]
    return products[skip:skip + limit]

@app.get("/api/v1/clients")
async def get_clients(skip: int = 0, limit: int = 100):
    """Get all clients (mock data for now)."""
    clients = [
        {
            "id": 1,
            "name": "Juan Pérez",
            "email": "juan@example.com",
            "phone": "+1234567890",
            "created_at": "2024-01-15T10:30:00Z"
        },
        {
            "id": 2,
            "name": "María García",
            "email": "maria@example.com",
            "phone": "+0987654321",
            "created_at": "2024-01-16T14:20:00Z"
        }
    ]
    return clients[skip:skip + limit]

@app.get("/api/v1/orders")
async def get_orders(skip: int = 0, limit: int = 100):
    """Get all orders (mock data for now)."""
    orders = [
        {
            "id": 1,
            "client_id": 1,
            "client_name": "Juan Pérez",
            "total_amount": 1299.99,
            "status": "completed",
            "created_at": "2024-01-20T09:15:00Z"
        },
        {
            "id": 2,
            "client_id": 2,
            "client_name": "María García",
            "total_amount": 139.98,
            "status": "pending",
            "created_at": "2024-01-21T11:45:00Z"
        }
    ]
    return orders[skip:skip + limit]
# --- FIN ENDPOINTS DE EJEMPLO ---

@app.get("/api/v1/cors-test")
async def cors_test(request: Request):
    """Test endpoint to verify CORS is working by checking the Origin header."""
    request_origin = request.headers.get("origin")
    return {
        "message": "CORS test endpoint",
        "request_origin": request_origin,
        "allowed_origins": ALLOWED_ORIGINS,
        "cors_working": request_origin in ALLOWED_ORIGINS if request_origin else False,
        "timestamp": "now"
    }

@app.options("/api/v1/cors-test")
async def cors_test_options():
    """Handle OPTIONS request for CORS test (preflight)."""
    return {}
