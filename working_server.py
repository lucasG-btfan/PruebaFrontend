# working_server.py
"""
Servidor funcional con todos los endpoints.
"""
import os
import sys
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="Ecommerce API",
    description="API funcional con base de datos",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar después de configurar
from config.database_render import SessionLocal
from services.client_service import ClientService
from schemas.client_schema import ClientCreateSchema

# Dependencia de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Ecommerce API is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ecommerce-api"}

@app.get("/test-db")
async def test_db(db: Session = Depends(get_db)):
    """Probar conexión a base de datos."""
    try:
        result = db.execute("SELECT version()").fetchone()
        return {
            "database": "connected",
            "postgres_version": result[0] if result else "unknown"
        }
    except Exception as e:
        return {"database": "error", "message": str(e)}

@app.get("/api/v1/clients")
async def get_clients(db: Session = Depends(get_db)):
    """Obtener todos los clientes."""
    try:
        service = ClientService(db)
        clients = service.get_all()
        return {"success": True, "data": clients, "count": len(clients)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/v1/clients")
async def create_client(client_data: ClientCreateSchema, db: Session = Depends(get_db)):
    """Crear un nuevo cliente."""
    try:
        service = ClientService(db)
        client = service.create(client_data)
        return {"success": True, "data": client, "message": "Client created"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/v1/clients/{client_id}")
async def get_client(client_id: int, db: Session = Depends(get_db)):
    """Obtener un cliente por ID."""
    try:
        service = ClientService(db)
        client = service.get_by_id(client_id)
        if client:
            return {"success": True, "data": client}
        else:
            return {"success": False, "error": "Client not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FULL server on http://localhost:8000")
    print("📊 Available endpoints:")
    print("  GET /                     - Welcome")
    print("  GET /health              - Health check")
    print("  GET /test-db             - Test database")
    print("  GET /api/v1/clients      - List all clients")
    print("  POST /api/v1/clients     - Create client")
    print("  GET /api/v1/clients/{id} - Get client by ID")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)