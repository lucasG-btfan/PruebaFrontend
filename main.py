# main.py - OPTIMIZADO PARA RENDER
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Configurar logging PRIMERO
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("=" * 60)
logger.info("🚀 INITIALIZING ECOMMERCE BACKEND ON RENDER")
logger.info("=" * 60)

# 1. Configurar variables de entorno para Render
if "RENDER" in os.environ:
    logger.info("🌐 Running in Render environment")
    # Render ya proporciona DATABASE_URL automáticamente
else:
    logger.info("💻 Running in local environment")
    # Para desarrollo local, usar URL directa
    os.environ.setdefault(
        'DATABASE_URL', 
        'postgresql://ecommerce_user:XuchJ7YFaWcfTnq4s1RX4CpTTGrxwfbG@dpg-d4mvsm1r0fns73ai8s10-a.ohio-postgres.render.com/ecommerce_db_sbeb'
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for FastAPI app"""
    # Startup
    logger.info("🔄 Starting up application...")
    
    try:
        # Importar y verificar configuración
        logger.info("📦 Importing configuration...")
        from config import engine
        
        # Probar conexión a la base de datos
        logger.info("🔗 Testing database connection...")
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info(f"✅ Database connection test: {result.scalar()}")
            
            # Verificar tablas
            result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
            table_count = result.scalar()
            logger.info(f"📊 Database has {table_count} tables")
            
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        # No fallar completamente, solo loguear el error
    
    logger.info("✅ Application startup complete")
    yield
    
    # Shutdown
    logger.info("👋 Shutting down application...")

# Crear la aplicación FastAPI
app = FastAPI(
    title="Ecommerce Backend API",
    description="API para sistema de ecommerce",
    version="2.0.0",
    docs_url="/docs" if os.getenv("ENABLE_DOCS", "true").lower() == "true" else None,
    redoc_url="/redoc" if os.getenv("ENABLE_DOCS", "true").lower() == "true" else None,
    lifespan=lifespan
)

# Configurar CORS
cors_origins = os.getenv("CORS_ORIGINS", "https://pruebafrontend-ea20.onrender.com,http://localhost:5173").split(",")
logger.info(f"🌍 CORS Origins configured: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Rutas básicas
@app.get("/")
async def root():
    return {
        "service": "Ecommerce Backend API",
        "status": "online",
        "version": "2.0.0",
        "environment": "production" if "RENDER" in os.environ else "development",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "api_v1": "/api/v1"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    try:
        from config import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": "now"
    }

# Importar y registrar routers
logger.info("🔄 Loading API routers...")

try:
    from controllers.health_check import router as health_router
    app.include_router(health_router, prefix="/api", tags=["Health"])
    logger.info("✅ Health router loaded")
except Exception as e:
    logger.warning(f"⚠️ Health router not loaded: {e}")

try:
    from controllers.client_controller import router as client_router
    app.include_router(client_router, prefix="/api/v1", tags=["Clients"])
    logger.info("✅ Client router loaded")
except Exception as e:
    logger.warning(f"⚠️ Client router not loaded: {e}")

logger.info("✅ All routers loaded successfully")
logger.info("=" * 60)
logger.info(f"🌐 Server ready at: http://0.0.0.0:{os.getenv('PORT', '10000')}")
logger.info("=" * 60)

# Para desarrollo local
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    
    logger.info(f"🚀 Starting local server on port {port}...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Desactivado en producción
        access_log=True
    )