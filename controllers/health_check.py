from fastapi import APIRouter
import time
from datetime import datetime
from database_render import check_connection

router = APIRouter()
# En controllers/health_check.py, modifica el endpoint raíz

@router.get("/")
def health_check():
    """Simple health check for quick response"""
    try:
        # Solo verificación básica de DB
        start = time.time()
        db_status = check_connection()
        db_latency_ms = round((time.time() - start) * 1000, 2)
        
        return {
            "status": "healthy" if db_status else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "database": {
                "status": "up" if db_status else "down",
                "latency_ms": db_latency_ms
            },
            "message": "Basic health check passed" if db_status else "Database connection failed"
        }
    except Exception as e:
        return {
            "status": "critical",
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Health check error: {str(e)}"
        }

@router.get("/simple")
def simple_health_check():
    """Ultra-fast health check"""
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow().isoformat(),
        "message": "API is running"
    }

# Endpoint completo separado
@router.get("/detailed")
def detailed_health_check():
    """Detailed health check with all components"""
    # Tu implementación actual aquí