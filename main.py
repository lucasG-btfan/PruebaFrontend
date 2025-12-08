import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Ecommerce Backend API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar CORS dinámicamente
def get_cors_origins():
    """Get CORS origins from environment or use defaults"""
    cors_env = os.getenv("CORS_ORIGINS", "")
    if cors_env:
        origins = [origin.strip() for origin in cors_env.split(",") if origin.strip()]
    else:
        origins = [
            "http://localhost:5173",
            "http://localhost:3000",
            "https://pruebafrontend-ea20.onrender.com"
        ]
    
    # Añadir el dominio propio para permitir llamadas internas
    if "RENDER" in os.environ:
        service_name = os.getenv("RENDER_SERVICE_NAME", "")
        if service_name:
            origins.append(f"https://{service_name}.onrender.com")
    
    logger.info(f"CORS origins configured: {origins}")
    return origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Verificar base de datos al inicio
@app.on_event("startup")
async def startup_event():
    try:
        from config.database import check_connection, initialize_models
        logger.info("🚀 Starting Ecommerce Backend...")
        
        if check_connection():
            logger.info("✅ Database connection successful")
            initialize_models()
        else:
            logger.warning("⚠️ Database connection failed - running in degraded mode")
            
    except Exception as e:
        logger.error(f"Startup error: {e}")
        logger.warning("Continuing despite startup errors")

# Endpoints básicos
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
    from config.database import check_connection
    return {
        "status": "healthy",
        "database": "connected" if check_connection() else "disconnected"
    }

# Importar y registrar routers después de crear la app
from controllers.product_controller import router as product_router
from controllers.order_controller import router as order_router
from controllers.bill_controller import router as bill_router

app.include_router(product_router, prefix="/api/v1")
app.include_router(order_router, prefix="/api/v1")
app.include_router(bill_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    logger.info(f"🚀 Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)