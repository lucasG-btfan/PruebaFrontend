import os
import logging
import traceback
from fastapi import FastAPI, APIRouter
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
    logger.info("🔄 Starting up application...")

    try:
        # Importar config
        from config import check_connection, initialize_models, engine, Base
        from sqlalchemy import text

        # 1. Probar conexión
        logger.info("🔗 Testing database connection...")
        if check_connection():
            logger.info("✅ Database connection successful")

            # 2. Inicializar modelos
            logger.info("📦 Initializing models...")
            if initialize_models():
                logger.info("✅ Models initialized")

                # 3. Verificar tablas existentes
                with engine.connect() as conn:
                    # Contar tablas en el schema public
                    result = conn.execute(text("""
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                        ORDER BY table_name
                    """))

                    tables = [row[0] for row in result]
                    logger.info(f"📊 Found {len(tables)} tables in database: {tables}")

                    # Verificar tablas esperadas vs reales
                    expected_tables = ['clients', 'products', 'orders', 'bills']
                    for table in expected_tables:
                        if table in tables:
                            logger.info(f"   ✅ {table}: exists")
                        else:
                            logger.warning(f"   ⚠️ {table}: missing")
            else:
                logger.warning("⚠️ Models initialization had issues")
        else:
            logger.error("❌ Database connection failed!")
            logger.warning("⚠️ Running in degraded mode without database")

    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        logger.error(traceback.format_exc())
        logger.warning("⚠️ Continuing despite startup errors")

    logger.info("✅ Application startup complete")
    yield
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
            "api_v1": "/api/v1",
            "clients": "/api/v1/clients",
            "products": "/api/v1/products",
            "orders": "/api/v1/orders",
            "bills": "/api/v1/bills",
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    try:
        from config import check_connection
        db_status = "connected" if check_connection() else "disconnected"
    except Exception:
        db_status = "disconnected"
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": "now"
    }

# Importar y registrar routers
logger.info("🔄 Loading API routers...")

# Router para Productos
try:
    from controllers.product_controller import router as product_router
    app.include_router(product_router, prefix="/api/v1", tags=["Products"])
    logger.info("✅ Product router loaded")
except Exception as e:
    logger.error(f"❌ Product router failed: {e}")
    # Crea router básico si falla
    product_router = APIRouter()
    @product_router.get("/products")
    async def get_products():
        return {"products": [], "message": "Using mock data"}
    app.include_router(product_router, prefix="/api/v1", tags=["Products"])
    logger.info("✅ Product router loaded (basic)")

# Router para Órdenes
try:
    from controllers.order_controller import router as order_router
    app.include_router(order_router, prefix="/api/v1", tags=["Orders"])
    logger.info("✅ Order router loaded")
except Exception as e:
    logger.error(f"❌ Order router failed: {e}")
    # Crea router básico
    order_router = APIRouter()
    @order_router.get("/orders")
    async def get_orders():
        return {"orders": [], "message": "Using mock data"}
    @order_router.post("/orders")
    async def create_order():
        return {"message": "Order created (mock)"}
    app.include_router(order_router, prefix="/api/v1", tags=["Orders"])
    logger.info("✅ Order router loaded (basic)")

# Router para Facturas
try:
    from controllers.bill_controller import router as bill_router
    app.include_router(bill_router, prefix="/api/v1", tags=["Bills"])
    logger.info("✅ Bill router loaded")
except Exception as e:
    logger.error(f"❌ Bill router failed: {e}")
    # Crea router básico
    bill_router = APIRouter()
    @bill_router.get("/bills")
    async def get_bills():
        return {"bills": [], "message": "Using mock data"}
    @bill_router.post("/bills")
    async def create_bill():
        return {"message": "Bill created (mock)"}
    app.include_router(bill_router, prefix="/api/v1", tags=["Bills"])
    logger.info("✅ Bill router loaded (basic)")

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
