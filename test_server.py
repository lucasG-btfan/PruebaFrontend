# test_server.py - VERSIÓN FINAL
"""
Simple test server to check basic functionality.
"""
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import signal
import sys

# IMPORTANTE: Establecer la variable de entorno ANTES de importar config
os.environ['DATABASE_URL'] = 'postgresql://ecommerce_user:XuchJ7YFaWcfTnq4s1RX4CpTTGrxwfbG@dpg-d4mvsm1r0fns73ai8s10-a.ohio-postgres.render.com/ecommerce_db_sbeb'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ahora importar config y otros módulos
from config import engine, SessionLocal, get_db

app = FastAPI(
    title="Test API",
    description="Test API for debugging",
    version="1.0.0"
)

# Configurar CORS básico
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Para testing, luego restringe
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Test API is running", "status": "online"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": "now"}

@app.get("/test-db")
async def test_db():
    """Test database connection"""
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            
            # Contar tablas
            result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
            table_count = result.scalar()
            
            return {
                "db_status": "connected",
                "postgres_version": version,
                "tables_count": table_count,
                "message": "Database connection successful"
            }
    except Exception as e:
        return {"db_status": "error", "message": str(e)}

@app.get("/api/test/clients")
async def test_clients():
    """Test clients endpoint"""
    try:
        from sqlalchemy import text
        from sqlalchemy.orm import Session
        
        db = SessionLocal()
        try:
            # Contar clientes
            result = db.execute(text("SELECT COUNT(*) FROM clients"))
            count = result.scalar()
            
            # Obtener algunos clientes
            result = db.execute(text("SELECT id_key, email FROM clients LIMIT 5"))
            clients = [{"id": row[0], "email": row[1]} for row in result]
            
            return {
                "total_clients": count,
                "sample_clients": clients,
                "status": "success"
            }
        finally:
            db.close()
    except Exception as e:
        return {"error": str(e), "status": "error"}

def signal_handler(sig, frame):
    logger.info("👋 Received shutdown signal")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("=" * 50)
    logger.info("🚀 TEST SERVER STARTING")
    logger.info("=" * 50)
    logger.info("🌍 Server: http://localhost:8000")
    logger.info("📊 Endpoints disponibles:")
    logger.info("  • GET / - Welcome page")
    logger.info("  • GET /health - Health check")
    logger.info("  • GET /test-db - Test database connection")
    logger.info("  • GET /api/test/clients - Test clients endpoint")
    logger.info("=" * 50)
    
    try:
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000, 
            reload=False,
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")