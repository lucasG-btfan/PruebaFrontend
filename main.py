import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import sys
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("=" * 60)
logger.info("INICIANDO APLICACIÓN")
logger.info("=" * 60)

try:
    from schemas.model_setup import rebuild_models, verify_schemas

    logger.info("Verificando schemas...")
    if verify_schemas():
        logger.info("✓ Schemas verificados correctamente")

    logger.info("Reconstruyendo modelos...")
    if rebuild_models():
        logger.info("✓ Modelos reconstruidos correctamente")
    else:
        logger.warning("⚠ Algunos modelos no se pudieron reconstruir")

except Exception as e:
    logger.error(f"✗ ERROR EN SCHEMAS: {e}", exc_info=True)

app = FastAPI(
    title="Ecommerce Backend API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

def get_cors_origins():
    """Get CORS origins from environment or use defaults"""
    cors_env = os.getenv("CORS_ORIGINS", "")
    origins = []

    default_origins = [
        "https://pruebafrontend-ea20.onrender.com",
        "https://comercio-digital.onrender.com"
    ]

    local_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080"
    ]

    if cors_env:
        origins.extend([origin.strip() for origin in cors_env.split(",") if origin.strip()])

    origins.extend(default_origins)
    origins.extend(local_origins)
    origins = list(set(origins))

    logger.info(f"CORS origins configured: {len(origins)} origins")
    return origins

@app.get("/debug-test")
async def debug_test():
    return {
        "message": "FastAPI debug endpoint",
        "status": "working",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/debug-db")
async def debug_db():
    try:
        from config.database import check_connection
        db_ok = check_connection()
        return {
            "message": "Database test",
            "database_connected": db_ok,
            "config_module": "config.database"
        }
    except Exception as e:
        return {
            "error": str(e),
            "type": type(e).__name__,
            "config_module": "ERROR"
        }

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

@app.get("/api/v1/debug/routes")
async def debug_routes():
    """Endpoint para debug de todas las rutas registradas"""
    routes = []
    for route in app.routes:
        if hasattr(route, "methods"):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name if hasattr(route, "name") else "N/A"
            })
    return {"routes": routes}

@app.get("/api/v1/docs/json")
async def openapi_json():
    """Ver el esquema OpenAPI completo"""
    return app.openapi()

@app.on_event("startup")
async def startup_event():
    try:
        from config.database import check_connection, create_tables, initialize_models
        logger.info("🚀 Starting Ecommerce Backend...")

        if check_connection():
            logger.info("✅ Database connection successful")

            # Crear tablas
            logger.info("🔨 Creating database tables...")
            if create_tables():
                logger.info("✅ Tables created successfully")
            else:
                logger.error("❌ Failed to create tables")

            initialize_models()
        else:
            logger.warning("⚠️ Database connection failed - running in degraded mode")

    except Exception as e:
        logger.error(f"❌ Startup error: {e}", exc_info=True)
        logger.warning("⚠️ Continuing despite startup errors")

@app.get("/")
async def root():
    return {
        "service": "Ecommerce Backend API",
        "status": "online",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
@app.get("/health_check")
async def health_check():
    """Health check endpoint para Render"""
    try:
        from config.database import check_connection
        db_status = "connected" if check_connection() else "disconnected"
    except Exception:
        db_status = "error"

    return {
        "status": "healthy",
        "database": db_status
    }

logger.info("Importando routers...")

try:
    from controllers.product_controller import router as product_router
    from controllers.order_controller import router as order_router
    from controllers.client_controller import router as client_router
    from controllers.auth_controller import router as auth_router
    from controllers.address_controller import router as address_router
    from controllers.bill_controller import router as bill_router
    from controllers.review_controller import router as review_router

    logger.info("✓ Routers importados correctamente")

    # Registrar routers
    app.include_router(product_router, prefix="/api/v1", tags=["Products"])
    app.include_router(order_router, prefix="/api/v1", tags=["Orders"])
    app.include_router(client_router, prefix="/api/v1", tags=["Clients"])
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(address_router, prefix="/api/v1", tags=["Addresses"])
    app.include_router(bill_router, prefix="/api/v1", tags=["Bills"])
    app.include_router(review_router, prefix="/api/v1", tags=["Reviews"])

    logger.info("✓ Routers registrados correctamente")

except Exception as e:
    logger.error(f"✗ Error importando/registrando routers: {e}", exc_info=True)
    raise

logger.info("=" * 60)
logger.info("VERIFICANDO RUTAS REGISTRADAS:")
logger.info("=" * 60)

# Contar rutas por router
router_counts = {}
all_routes = []

for route in app.routes:
    if hasattr(route, "methods"):
        path = route.path
        methods = list(route.methods)
        
        # Filtrar rutas de reviews
        if "/reviews" in path:
            logger.info(f"✅ REVIEW ROUTE: {methods} {path}")
        
        all_routes.append({"path": path, "methods": methods})

logger.info(f"Total de rutas registradas: {len(all_routes)}")

# Verificar específicamente las rutas de reviews
review_routes = [r for r in all_routes if "/reviews" in r["path"]]
if review_routes:
    logger.info(f"✓ Rutas de reviews encontradas: {len(review_routes)}")
    for route in review_routes:
        logger.info(f"  - {route['methods']} {route['path']}")
else:
    logger.error("✗ NO SE ENCONTRARON RUTAS DE REVIEWS!")
    
    # Debug adicional: verificar el router de reviews
    logger.info("Debug del router de reviews:")
    try:
        for route in review_router.routes:
            if hasattr(route, "methods"):
                logger.info(f"  En router: {list(route.methods)} {route.path}")
    except Exception as e:
        logger.error(f"Error examinando router de reviews: {e}")

from controllers.client_controller import router as client_router
logger.info("Rutas en el router de clientes:")
for route in client_router.routes:
    logger.info(f" - {route.path}")

# if __name__ == "__main__":
#     import uvicorn
#     port = int(os.getenv("PORT", 10000))
#     logger.info(f"🚀 Starting server on port {port}")
#     uvicorn.run(app, host="0.0.0.0", port=port)