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
- Graceful error handling for missing modules
"""
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Basic logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import configuration
try:
    from config import constants
    logger.info("✅ Constants loaded from config.constants")
except ImportError as e:
    logger.warning(f"⚠️ Could not import constants: {e}")
    # Fallback constants
    class SimpleConstants:
        APP_NAME = "E-commerce API"
        APP_DESCRIPTION = "E-commerce REST API"
        APP_VERSION = "1.0.0"
        HOST = os.getenv("HOST", "0.0.0.0")
        PORT = int(os.getenv("PORT", "8000"))
        DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        ENABLE_DOCS = os.getenv("ENABLE_DOCS", "True").lower() == "true"
        ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
        API_V1_PREFIX = "/api/v1"

    constants = SimpleConstants()
    logger.info("✅ Using simple constants")

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

    # Database connection and table initialization
    try:
        from config.database_render import check_connection, create_tables
        if not check_connection():
            logger.critical("❌ Failed to establish database connection.")
            raise RuntimeError("Database connection failed")
        logger.info("✅ Database connection established")

        if not create_tables():
            logger.error("❌ Failed to initialize database tables")
        else:
            logger.info("✅ Database tables initialized")
    except ImportError as e:
        logger.warning(f"⚠️ Database module not available: {e}")
    except Exception as e:
        logger.error(f"❌ Database error: {e}")

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
load_middleware("middleware.request_id_middleware", "RequestIdMiddleware")
load_middleware("middleware.endpoint_rate_limiter", "EndpointRateLimiter")

# API Routers
def load_router(module_path: str, router_name: str, prefix: str, tag: str):
    """Dynamically load and add router with error handling."""
    try:
        module = __import__(module_path, fromlist=[router_name])
        router = getattr(module, router_name)
        app.include_router(router, prefix=prefix, tags=[tag])
        logger.info(f"✅ {tag} router loaded successfully")
    except Exception as e:
        logger.warning(f"⚠️ Failed to load {tag} router: {str(e)}")

# Load routers
load_router("controllers.health_check", "router", "", "Health")
load_router("controllers.client_controller", "router", constants.API_V1_PREFIX, "Clients")
load_router("controllers.product_controller", "router", constants.API_V1_PREFIX, "Products")
load_router("controllers.category_controller", "router", constants.API_V1_PREFIX, "Categories")
load_router("controllers.order_controller", "router", constants.API_V1_PREFIX, "Orders")

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
