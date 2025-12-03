# main.py
"""
Main FastAPI application.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar configuración y utilidades
from config import constants
from config.database_render import create_tables, check_connection
from config.logging_config import setup_logging
from middleware.request_id_middleware import RequestIdMiddleware
from middleware.endpoint_rate_limiter import EndpointRateLimiter

# Importar controladores ROUTERS (no los controladores completos)
from controllers.health_check import router as health_router
from controllers.client_controller import router as client_router
from controllers.product_controller import router as product_router
from controllers.category_controller import router as category_router
from controllers.order_controller import router as order_router
# Importar otros routers según sea necesario

# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Starting E-commerce API...")
    
    # Check database connection
    if check_connection():
        logger.info("✅ Database connection established")
    else:
        logger.error("❌ Database connection failed")
    
    # Create tables if they don't exist
    if create_tables():
        logger.info("✅ Database tables initialized")
    else:
        logger.error("❌ Failed to initialize database tables")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down E-commerce API...")


# Crear aplicación FastAPI
app = FastAPI(
    title=constants.APP_NAME,
    description=constants.APP_DESCRIPTION,
    version=constants.APP_VERSION,
    docs_url="/docs" if constants.ENABLE_DOCS else None,
    redoc_url="/redoc" if constants.ENABLE_DOCS else None,
    openapi_url="/openapi.json" if constants.ENABLE_DOCS else None,
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=constants.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Añadir middleware personalizado
app.add_middleware(RequestIdMiddleware)
app.add_middleware(EndpointRateLimiter)

# Registrar rutas
app.include_router(health_router, tags=["Health"])
app.include_router(client_router, prefix="/api/v1", tags=["Clients"])
app.include_router(product_router, prefix="/api/v1", tags=["Products"])
app.include_router(category_router, prefix="/api/v1", tags=["Categories"])
app.include_router(order_router, prefix="/api/v1", tags=["Orders"])
# Registrar otros routers...


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "E-commerce REST API",
        "version": constants.APP_VERSION,
        "docs": "/docs",
        "health": "/health_check"
    }


if __name__ == "__main__":
    import uvicorn
    logger.info(f"🌍 Starting server on {constants.HOST}:{constants.PORT}")
    uvicorn.run(
        "main:app",
        host=constants.HOST,
        port=constants.PORT,
        reload=constants.DEBUG,
        log_level="info"
    )