"""
Main application module for FastAPI e-commerce REST API.
This module initializes the FastAPI application, registers all routers,
and configures global exception handlers.
"""
import os
import uvicorn
import logging
import traceback
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from starlette.responses import JSONResponse
from sqlalchemy import inspect
from config.logging_config import setup_logging
from config.database_render import engine, get_db, Base
from config.redis_config import redis_client as redis_config, check_redis_connection
from middleware.rate_limiter import RateLimiterMiddleware
from middleware.request_id_middleware import RequestIDMiddleware

# Setup centralized logging FIRST
setup_logging()
logger = logging.getLogger(__name__)

# Import controllers
from controllers.address_controller import AddressController
from controllers.bill_controller import BillController
from controllers.category_controller import CategoryController
from controllers.client_controller import ClientController
from controllers.order_controller import OrderController
from controllers.order_detail_controller import OrderDetailController
from controllers.product_controller import ProductController
from controllers.review_controller import ReviewController
from controllers.health_check import router as health_check_controller
from repositories.base_repository_impl import InstanceNotFoundError

def create_fastapi_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    # API metadata
    fastapi_app = FastAPI(
        title="E-commerce REST API",
        description="FastAPI REST API for e-commerce system with PostgreSQL",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # CORS Configuration
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://pruebafrontend-ea20.onrender.com",
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "https://tu-frontend.onrender.com",  # Your frontend
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info(f"✅ CORS enabled for multiple origins")

    @fastapi_app.get("/")
    async def root():
        """Root endpoint with API information"""
        return {
            "message": "E-commerce REST API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health_check"
        }

    # Global exception handlers
    @fastapi_app.exception_handler(InstanceNotFoundError)
    async def instance_not_found_exception_handler(request, exc):
        """Handle InstanceNotFoundError with 404 response."""
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": str(exc)},
        )

    # Register controllers
    client_controller = ClientController()
    fastapi_app.include_router(client_controller.router, prefix="/clients")
    order_controller = OrderController()
    fastapi_app.include_router(order_controller.router, prefix="/orders")
    product_controller = ProductController()
    fastapi_app.include_router(product_controller.router, prefix="/products")
    address_controller = AddressController()
    fastapi_app.include_router(address_controller.router, prefix="/addresses")
    bill_controller = BillController()
    fastapi_app.include_router(bill_controller.router, prefix="/bills")
    order_detail_controller = OrderDetailController()
    fastapi_app.include_router(order_detail_controller.router, prefix="/order_details")
    review_controller = ReviewController()
    fastapi_app.include_router(review_controller.router, prefix="/reviews")
    category_controller = CategoryController()
    fastapi_app.include_router(category_controller.router, prefix="/categories")
    fastapi_app.include_router(health_check_controller, prefix="/health_check")

    # Request ID middleware runs FIRST (innermost) to capture all logs
    fastapi_app.add_middleware(RequestIDMiddleware)
    logger.info("✅ Request ID middleware enabled (distributed tracing)")

    # Rate limiting: 100 requests per 60 seconds per IP (configurable via env)
    fastapi_app.add_middleware(RateLimiterMiddleware, calls=100, period=60)
    logger.info("✅ Rate limiting enabled: 100 requests/60s per IP")

    @fastapi_app.on_event("startup")
    async def startup_event():
        """Run on application startup"""
        logger.info("🚀 Starting FastAPI E-commerce API...")

        # Crear database tables - FORZAR creación solo si no existen
        try:
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()
            logger.info(f"📊 Existing tables: {existing_tables}")

            if 'clients' not in existing_tables:
                logger.info("📦 The 'clients' table does not exist. Creating all tables...")
                Base.metadata.create_all(bind=engine)
                logger.info("✅ Database tables created successfully")
            else:
                logger.info("✅ The 'clients' table already exists")

        except Exception as e:
            logger.error(f"❌ Database error: {e}")
            logger.error(traceback.format_exc())

        # Check Redis connection
        if check_redis_connection():
            logger.info("✅ Redis cache is available")
        else:
            logger.warning("⚠️ Redis cache is NOT available - running without cache")

    @fastapi_app.on_event("shutdown")
    async def shutdown_event():
        """Graceful shutdown - close all connections"""
        logger.info("👋 Shutting down FastAPI E-commerce API...")

        # Close Redis connection
        try:
            redis_config.close()
            logger.info("✅ Redis connection closed")
        except Exception as e:
            logger.error(f"❌ Error closing Redis: {e}")

        # Close database engine
        try:
            engine.dispose()
            logger.info("✅ Database engine disposed")
        except Exception as e:
            logger.error(f"❌ Error disposing database engine: {e}")

        logger.info("✅ Shutdown complete")

    return fastapi_app

# ✅ CRÍTICO: Crear la instancia de app a nivel global
app = create_fastapi_app()

# ✅ ELIMINAR el bloque __main__ o hacerlo condicional
# Render no ejecuta __main__, solo importa 'app'
if __name__ == "__main__":
    # Solo para desarrollo local
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🚀 Starting local development server on port {port}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True  # Solo para desarrollo
    )
