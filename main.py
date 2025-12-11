import os
import logging
from fastapi import FastAPI,Request
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

def get_cors_origins():
    """Get CORS origins from environment or use defaults"""
    cors_env = os.getenv("CORS_ORIGINS", "")
    origins = []

    # Orígenes por defecto (frontend en Render)
    default_origins = [
        "https://pruebafrontend-ea20.onrender.com",
        "https://comercio-digital.onrender.com"
    ]

    # Orígenes locales para desarrollo
    local_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080"
    ]

    # Agregar orígenes desde la variable de entorno si existe
    if cors_env:
        origins.extend([origin.strip() for origin in cors_env.split(",") if origin.strip()])

    # Agregar orígenes por defecto y locales
    origins.extend(default_origins)
    origins.extend(local_origins)

    # Remover duplicados
    origins = list(set(origins))

    logger.info(f"CORS origins configured: {origins}")
    return origins

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

@app.post("/api/v1/admin/migrate-idkey") #endpoint temporal
async def migrate_idkey_endpoint(request: Request):
    """Endpoint para ejecutar migración a id_key"""
    # Proteger con API key en producción
    api_key = request.headers.get("X-API-KEY")
    if api_key != os.getenv("MIGRATION_KEY", "migration_temp_key"):
        return {"error": "Unauthorized"}, 401
    
    from sqlalchemy import text
    from config.database import SessionLocal
    
    db = SessionLocal()
    try:
        # Ejecutar migración paso a paso
        steps = []
        
        # Paso 1: Agregar columna si no existe
        db.execute(text("""
            ALTER TABLE clients 
            ADD COLUMN IF NOT EXISTS id_key INTEGER
        """))
        steps.append("Columna id_key agregada/verificada")
        
        # Paso 2: Poblar id_key
        db.execute(text("""
            UPDATE clients 
            SET id_key = COALESCE(id_key, id)
            WHERE id_key IS NULL OR id_key != id
        """))
        steps.append("id_key poblada con valores de id")
        
        # Paso 3: Hacer NOT NULL
        db.execute(text("""
            ALTER TABLE clients 
            ALTER COLUMN id_key SET NOT NULL
        """))
        steps.append("id_key marcada como NOT NULL")
        
        # Paso 4: Agregar UNIQUE constraint
        try:
            db.execute(text("""
                ALTER TABLE clients 
                ADD CONSTRAINT clients_id_key_unique UNIQUE (id_key)
            """))
            steps.append("Constraint UNIQUE agregada")
        except:
            steps.append("Constraint UNIQUE ya existía")
        
        db.commit()
        
        return {
            "success": True,
            "steps": steps,
            "message": "Migración iniciada. Ahora actualiza tus modelos."
        }
        
    except Exception as e:
        db.rollback()
        return {"error": str(e)}, 500
    finally:
        db.close()

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
from controllers.client_controller import router as client_router

app.include_router(product_router, prefix="/api/v1/products")
app.include_router(order_router, prefix="/api/v1/orders")
app.include_router(bill_router, prefix="/api/v1/bills")
app.include_router(client_router, prefix="/api/v1/clients")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    logger.info(f"🚀 Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
