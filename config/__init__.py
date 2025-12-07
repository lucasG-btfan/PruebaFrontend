# config/__init__.py - SIMPLIFICADO
"""
Configuration package initialization.
Exports only what's needed to avoid import issues.
"""

import os
import logging

logger = logging.getLogger(__name__)

# Exportaciones principales
try:
    from .database_render import (
        engine,
        SessionLocal,
        get_db,
        create_tables,
        check_connection,
        initialize_models
    )
    
    # Obtener DATABASE_URL
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    
    logger.info(f"✅ Database config loaded successfully")
    logger.info(f"📦 Database URL available: {bool(DATABASE_URL)}")
    
except ImportError as e:
    logger.error(f"❌ Failed to import database configuration: {e}")
    # Crear stubs para evitar crashes
    engine = None
    SessionLocal = None
    get_db = None
    DATABASE_URL = ""
    
    def create_tables():
        logger.error("create_tables() called but database not configured")
        return False
    
    def check_connection():
        logger.error("check_connection() called but database not configured")
        return False
    
    def initialize_models():
        logger.error("initialize_models() called but database not configured")
        return False

__all__ = [
    'engine',
    'SessionLocal', 
    'get_db',
    'create_tables',
    'check_connection',
    'initialize_models',
    'DATABASE_URL'
]