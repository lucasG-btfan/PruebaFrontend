# config/database.py - VERSIÓN SIMPLIFICADA
"""
Database configuration wrapper.
"""
import os

# Importar todo desde database_render
from .database_render import (
    engine,
    SessionLocal,
    get_db,
    create_tables,
    check_connection,
    initialize_models
)

# Obtener DATABASE_URL del entorno
DATABASE_URL = os.getenv("DATABASE_URL", "")
DATABASE_URI = DATABASE_URL  # Alias para compatibilidad

if not DATABASE_URL:
    print("⚠️ DATABASE_URL environment variable is not set")
    print("📝 Using connection from database_render.py")

__all__ = [
    'engine',
    'SessionLocal',
    'get_db',
    'create_tables',
    'check_connection',
    'initialize_models',
    'DATABASE_URL',
    'DATABASE_URI',
]