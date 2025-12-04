"""
Configuration package initialization.
Exports database components and application constants for easy import.
"""
# Import constants
from config.constants import *

# Import database components
try:
    from config.database import engine, SessionLocal, get_db, create_tables, check_connection
except ImportError:
    # Si no existe database.py, usa database_render.py
    try:
        from config.database_render import engine, SessionLocal, get_db, create_tables, check_connection
    except ImportError:
        # Define valores por defecto
        engine = None
        SessionLocal = None
        get_db = None
        create_tables = None
        check_connection = None