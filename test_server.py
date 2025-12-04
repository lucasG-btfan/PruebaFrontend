# test_server.py
"""
Simple test server to check basic functionality.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Importar routers
from controllers.client_controller import router as client_router
from controllers.health_check import router as health_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Test API",
    description="Test API for debugging",
    version="1.0.0"
)

# Configurar CORS básico
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas básicas
app.include_router(health_router, tags=["Health"])
app.include_router(client_router, prefix="/api/v1", tags=["Clients"])

@app.get("/")
async def root():
    return {"message": "Test API is running"}

if __name__ == "__main__":
    logger.info("🌍 Starting test server on localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)