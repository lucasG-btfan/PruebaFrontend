"""
E-commerce FastAPI Application

Main entry point for the E-commerce REST API.
Features:
- Lifespan management for startup/shutdown tasks
- CORS configuration
- Custom middleware integration
- API routers organization
- Health check and root endpoints
- Database connection and table initialization
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configuration
from config import constants
from config.logging_config import setup_logging

# Setup logging configuration
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Handles startup and shutdown events:
    - Database connection verification
    - Table initialization
    - Resource cleanup
    """
    logger.info("🚀 Starting E-commerce API...")

    # Lazy import to avoid circular dependencies
    from config.database_render import check_connection, create_tables

    # Verify database connection
    if not check_connection():
        logger.critical("❌ Failed to establish database connection. Exiting...")
        raise RuntimeError("Database connection failed")

    logger.info("✅ Database connection established")

    # Initialize database tables
    if not create_tables():
        logger.error("❌ Failed to initialize database tables")
    else:
        logger.info("✅ Database tables initialized")

    yield  # Application runs here

    logger.info("👋 Shutting down E-commerce API...")

# Create FastAPI application
app = FastAPI(
    title=constants.APP_NAME,
    description=constants.APP_DESCRIPTION,
    version=constants.APP_VERSION,
    docs_url="/docs" if constants.ENABLE_DOCS else None,
    redoc_url="/redoc" if constants.ENABLE_DOCS else None,
    openapi_url="/openapi.json" if constants.ENABLE_DOCS else None,
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=constants.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware Integration
def load_middleware(middleware_path: str, middleware_name: str):
    """Dynamically load and add middleware with error handling."""
    try:
        module = __import__(middleware_path, fromlist=[middleware_name])
        middleware_class = getattr(module, middleware_name)
        app.add_middleware(middleware_class)
        logger.info(f"✅ {middleware_name} loaded successfully")
    except Exception as e:
        logger.warning(f"⚠️ Failed to load {middleware_name}: {str(e)}")

# Load custom middlewares
load_middleware("middleware.request_id_middleware", "RequestIDMiddleware")
load_middleware("middleware.endpoint_rate_limiter", "EndpointRateLimiter")

# API Routers
from controllers.health_check import router as health_router
from controllers.client_controller import router as client_router
from controllers.product_controller import router as product_router
from controllers.category_controller import router as category_router
from controllers.order_controller import router as order_router

app.include_router(health_router, tags=["Health"])
app.include_router(client_router, prefix="/api/v1", tags=["Clients"])
app.include_router(product_router, prefix="/api/v1", tags=["Products"])
app.include_router(category_router, prefix="/api/v1", tags=["Categories"])
app.include_router(order_router, prefix="/api/v1", tags=["Orders"])

@app.get("/", summary="API Root Endpoint", response_model=dict)
async def root():
    """
    Root endpoint providing basic API information.
    Returns:
        dict: API metadata and useful links
    """
    return {
        "message": "E-commerce REST API",
        "version": constants.APP_VERSION,
        "docs": "/docs" if constants.ENABLE_DOCS else None,
        "health": "/health_check",
        "status": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info(f"🌍 Starting server on {constants.HOST}:{constants.PORT}")
    uvicorn.run(
        "main:app",
        host=constants.HOST,
        port=constants.PORT,
        reload=constants.DEBUG,
        log_level="info",
    )
