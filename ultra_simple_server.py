"""
Servidor ultra simple que evita todos los problemas de importación.
"""
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configurar path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="Ecommerce API - Simple",
    description="Versión simple sin problemas de importación",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "API Simple Funcionando!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/test-db-simple")
async def test_db_simple():
    """Probar conexión a DB sin importaciones complejas."""
    try:
        # Importar directamente lo necesario
        from sqlalchemy import create_engine, text
        
        # Usar URL directa (cámbiala si es diferente)
        DATABASE_URL = "postgresql://ecommerce_user:XuchJ7YFaWcfTnq4s1RX4CpTTGrxwfbG@dpg-d4mvsm1r0fns73ai8s10-a.ohio-postgres.render.com/ecommerce_db_sbeb"
        
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            
            # También verificar tablas
            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            tables = [row[0] for row in result]
            
            return {
                "status": "connected",
                "postgres_version": version,
                "tables": tables,
                "table_count": len(tables)
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/simple/clients")
async def get_clients_simple():
    """Obtener clientes directamente con SQL."""
    try:
        from sqlalchemy import create_engine, text
        
        DATABASE_URL = "postgresql://ecommerce_user:XuchJ7YFaWcfTnq4s1RX4CpTTGrxwfbG@dpg-d4mvsm1r0fns73ai8s10-a.ohio-postgres.render.com/ecommerce_db_sbeb"
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM clients LIMIT 10"))
            clients = []
            for row in result:
                clients.append({
                    "id": row.id_key,
                    "full_name": row.full_name,
                    "email": row.email,
                    "phone": row.phone,
                    "is_active": row.is_active
                })
            
            return {
                "success": True,
                "count": len(clients),
                "clients": clients
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    print("🚀 ULTRA SIMPLE SERVER starting...")
    print("📊 Endpoints disponibles:")
    print("  GET /                    - Welcome")
    print("  GET /health             - Health check")
    print("  GET /test-db-simple     - Test database (directo)")
    print("  GET /api/simple/clients - Get clients (direct SQL)")
    print("\n🌐 Abre: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)