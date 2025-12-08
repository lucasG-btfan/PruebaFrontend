#!/usr/bin/env python3
"""
ULTRA-SIMPLIFIED Production server for Render.
"""
import os
import sys
import logging

# Configure logging FIRST
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("=" * 60)
logger.info("🚀 ULTRA SIMPLE PRODUCTION SERVER FOR RENDER")
logger.info("=" * 60)

# 1. Set environment variables for Render
if "RENDER" in os.environ:
    logger.info("🌐 Running on Render cloud")
    # Force database URL for Render
    os.environ["DATABASE_URL"] = os.getenv(
        "DATABASE_URL", 
        "postgresql://ecommerce_user:XuchJ7YFaWcfTnq4s1RX4CpTTGrxwfbG@dpg-d4mvsm1r0fns73ai8s10-a.ohio-postgres.render.com/ecommerce_db_sbeb"
    )
else:
    logger.info("💻 Running locally")

# 2. DIRECT database test BEFORE any complex imports
logger.info("🔍 Direct database connection test...")
try:
    # Import ONLY what we need for the test
    from sqlalchemy import create_engine, text
    
    db_url = os.getenv("DATABASE_URL")
    logger.info(f"📦 Database URL: {db_url[:50]}...")
    
    # Create simple engine
    engine = create_engine(db_url, connect_args={"sslmode": "require"})
    
    # Test connection
    with engine.connect() as conn:
        # Use text() explicitly
        result = conn.execute(text("SELECT 1 as test"))
        row = result.fetchone()
        logger.info(f"✅ DIRECT DB TEST: {row[0]}")
        
except Exception as e:
    logger.error(f"❌ DIRECT DB TEST FAILED: {e}")
    import traceback
    logger.error(traceback.format_exc())

# 3. Now import FastAPI
try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    logger.info("✅ FastAPI imported")
except Exception as e:
    logger.error(f"❌ Failed to import FastAPI: {e}")
    sys.exit(1)

# 4. Create minimal app
app = FastAPI(
    title="Ecommerce API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 5. Simple CORS - allow everything for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 6. Health check endpoint
@app.get("/health")
async def health_check():
    """Ultra-simple health check"""
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(os.getenv("DATABASE_URL"))
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "degraded", "database": "disconnected", "error": str(e)}

# 7. Root endpoint
@app.get("/")
async def root():
    return {"message": "Ecommerce API", "status": "online"}

# 8. Load actual routers SAFELY
logger.info("🔄 Loading API routers...")

try:
    # Try to load product router
    from controllers.product_controller import router as product_router
    app.include_router(product_router, prefix="/api/v1", tags=["products"])
    logger.info("✅ Product router loaded")
except Exception as e:
    logger.error(f"❌ Product router failed: {e}")
    # Create fallback
    from fastapi import APIRouter
    product_router = APIRouter()
    @product_router.get("/products")
    async def get_products():
        return {"products": [], "message": "fallback"}
    app.include_router(product_router, prefix="/api/v1", tags=["products"])
    logger.info("✅ Product router (fallback)")

try:
    # Try to load order router
    from controllers.order_controller import router as order_router
    app.include_router(order_router, prefix="/api/v1", tags=["orders"])
    logger.info("✅ Order router loaded")
except Exception as e:
    logger.error(f"❌ Order router failed: {e}")
    # Create fallback
    from fastapi import APIRouter
    order_router = APIRouter()
    @order_router.get("/orders")
    async def get_orders():
        return {"orders": []}
    app.include_router(order_router, prefix="/api/v1", tags=["orders"])
    logger.info("✅ Order router (fallback)")

logger.info("=" * 60)
logger.info(f"✅ Server ready on port {os.getenv('PORT', '10000')}")
logger.info("=" * 60)

# 9. Run server
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "10000"))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )