#!/usr/bin/env python3
"""
Production server runner optimized for Render.
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
logger.info("🚀 PRODUCTION SERVER STARTING")
logger.info("=" * 60)

# 1. Check if running on Render
if "RENDER" in os.environ:
    logger.info("🌐 Running on Render Platform")
    
    # Force critical environment variables
    if not os.getenv("DATABASE_URL"):
        logger.warning("⚠️ DATABASE_URL not found, using default")
        os.environ["DATABASE_URL"] = "postgresql://ecommerce_db_pg18_user:8wj5MwKBGSfrK3ZG6vADvjT5pkc4ai7u@dpg-d4riokmr433s73a9vb70-a.ohio-postgres.render.com/ecommerce_db_pg18"
    
    # Set PORT for Render
    if not os.getenv("PORT"):
        os.environ["PORT"] = "10000"
else:
    logger.info("💻 Running in local environment")

# 2. Test database connection with minimal imports
logger.info("🔍 Testing database connection...")
try:
    # Import ONLY sqlalchemy core
    from sqlalchemy import create_engine, text
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL is not set")
    
    logger.info(f"📦 Database URL: {db_url[:50]}...")
    
    # Create engine with SSL for Render
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={
            "sslmode": "require",
            "connect_timeout": 10
        }
    )
    
    # Execute test query
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1 as test_value"))
        test_result = result.scalar()
        logger.info(f"✅ Database connection successful: {test_result}")
        
        # Check PostgreSQL version
        result = conn.execute(text("SELECT version()"))
        version = result.scalar()
        logger.info(f"📊 PostgreSQL: {version.split(',')[0]}")
        
except Exception as e:
    logger.error(f"❌ Database connection failed: {e}")
    # Don't exit, continue in degraded mode

# 3. Import main app
try:
    from main import app
    logger.info("✅ Main application imported successfully")
    
    # Add health check endpoint if not present
    from fastapi import FastAPI
    
    @app.get("/health_check")
    async def health_check():
        return {
            "status": "healthy",
            "service": "ecommerce-api",
            "environment": "production" if "RENDER" in os.environ else "development"
        }
        
except Exception as e:
    logger.error(f"❌ Failed to import main application: {e}")
    sys.exit(1)

logger.info("=" * 60)
logger.info(f"✅ Server ready on port {os.getenv('PORT', '10000')}")
logger.info("=" * 60)

# 4. Run server
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "10000"))
    host = "0.0.0.0"
    
    logger.info(f"🚀 Starting Uvicorn on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        workers=int(os.getenv("UVICORN_WORKERS", "1")),
        log_level="info",
        access_log=True,
        timeout_keep_alive=30
    )