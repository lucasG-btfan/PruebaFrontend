"""
Configuration package initialization.
Exports database components and application constants for easy import.
"""

# Import constants
from config.constants import *

# Import database components - Versión simplificada y segura
try:
    # Intentar importar de database_render primero
    from config.database_render import engine, SessionLocal, get_db, check_connection
    
    # create_tables puede no existir en database_render
    try:
        from config.database_render import create_tables
    except ImportError:
        # Si no existe, definir una función dummy
        def create_tables():
            print("⚠️ create_tables not available in database_render")
            return False
    
except ImportError:
    print("⚠️ database_render not available, using database.py")
    try:
        from config.database import engine, SessionLocal, get_db, create_tables, check_connection
    except ImportError:
        # Define valores por defecto para desarrollo local
        print("⚠️ Neither database_render nor database is available. Using dummy values.")
        
        engine = None
        SessionLocal = None
        
        def get_db():
            """Dummy dependency"""
            yield None
        
        def create_tables():
            """Dummy function"""
            print("⚠️ No database available for table creation")
            return False
        
        def check_connection():
            """Dummy connection check"""
            print("⚠️ No database available for connection check")
            return False