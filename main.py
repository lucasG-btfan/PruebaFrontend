"""
Main FastAPI application - Simple version for production.
Uses centralized constants from simple_constants.py.
"""
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request # Se añadió 'Request'
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel # Importado para los modelos de Cliente
from typing import List # Importado para los modelos de Cliente

# Importar constantes centralizadas
from simple_constants import (
    APP_NAME,
    APP_DESCRIPTION,
    APP_VERSION,
    HOST,
    PORT,
    ENABLE_DOCS,
    ALLOWED_ORIGINS,
    LOG_LEVEL,
    LOG_FORMAT
)

# Configurar logging
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager."""
    logger.info("🚀 Starting E-commerce API...")
    # Intentar conectar a base de datos
    try:
        from config.database_render import check_connection, create_tables
        if check_connection():
            logger.info("✅ Database connected")
            create_tables()
            logger.info("✅ Tables created/verified")
    except Exception as e:
        logger.warning(f"⚠️ Database setup skipped: {e}")
    yield
    logger.info("👋 Shutting down...")

# Crear aplicación FastAPI
app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url="/docs" if ENABLE_DOCS else None,
    redoc_url="/redoc" if ENABLE_DOCS else None,
    openapi_url="/openapi.json" if ENABLE_DOCS else None,
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "E-commerce REST API",
        "version": APP_VERSION,
        "docs": "/docs",
        "health": "/health_check"
    }

# Health check endpoint
@app.get("/health_check")
async def health_check():
    return {"status": "healthy", "timestamp": "now"}

@app.get("/api/v1/cors-test")
async def cors_test(request: Request):
    """Test endpoint to verify CORS is working by checking the Origin header."""
    request_origin = request.headers.get("origin")
    return {
        "message": "CORS test endpoint",
        "request_origin": request_origin,
        "allowed_origins": ALLOWED_ORIGINS,
        "cors_working": request_origin in ALLOWED_ORIGINS if request_origin else False,
        "timestamp": "now"
    }

@app.options("/api/v1/cors-test")
async def cors_test_options():
    """Handle OPTIONS request for CORS test (preflight)."""
    # El CORSMiddleware de FastAPI maneja los encabezados de respuesta
    return {}

class ClientResponse(BaseModel):
    id_key: int
    name: str
    lastname: str
    email: str

class ClientListResponse(BaseModel):
    items: List[ClientResponse]
    total: int
    page: int
    size: int
    pages: int

# Simple clients endpoint
@app.get("/api/v1/clients", response_model=ClientListResponse)
async def get_clients(skip: int = 0, limit: int = 100):
    return {
        "items": [
            {"id_key": 1, "name": "John", "lastname": "Doe", "email": "john@example.com"},
            {"id_key": 2, "name": "Jane", "lastname": "Smith", "email": "jane@example.com"}
        ],
        "total": 2,
        "page": 1,
        "size": limit,
        "pages": 1
    }