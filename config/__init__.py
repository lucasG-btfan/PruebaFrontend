# config/__init__.py
"""
Configuration package initialization.
"""
import os
import logging

logger = logging.getLogger(__name__)

try:
    # ✅ Importar desde database
    from .database import (
        engine,
        SessionLocal,
        get_db,
        create_tables,
        check_connection,
        initialize_models,
        Base
    )
    
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    
    if DATABASE_URL:
        logger.info(f"✅ Database config loaded from environment")
    else:
        logger.warning("⚠️ DATABASE_URL not set, using default")
        
except ImportError as e:
    logger.error(f"❌ Failed to import database configuration: {e}")
    raise

__all__ = [
    'engine',
    'SessionLocal', 
    'get_db',
    'create_tables',
    'check_connection',
    'initialize_models',
    'DATABASE_URL',
    'Base'
]