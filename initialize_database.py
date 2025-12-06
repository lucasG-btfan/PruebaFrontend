# backend/initialize_database.py
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database_render import create_tables, check_connection, engine
from config.database_render import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Initialize database with tables and sample data."""
    
    # Verificar conexión
    if not check_connection():
        logger.error("❌ Cannot connect to database. Exiting.")
        return
    
    # Crear tablas
    if create_tables():
        logger.info("✅ Database tables created successfully")
    else:
        logger.error("❌ Failed to create database tables")
    
    # Opcional: Insertar datos de ejemplo
    try:
        from sqlalchemy.orm import Session
        from models.category import Category
        
        session = Session(bind=engine)
        
        # Verificar si ya hay categorías
        existing = session.query(Category).count()
        if existing == 0:
            # Insertar categorías de ejemplo
            categories = [
                Category(name="Electrónica", description="Productos electrónicos"),
                Category(name="Ropa", description="Ropa y accesorios"),
                Category(name="Hogar", description="Productos para el hogar"),
                Category(name="Deportes", description="Artículos deportivos"),
            ]
            
            session.add_all(categories)
            session.commit()
            logger.info(f"✅ Inserted {len(categories)} sample categories")
        else:
            logger.info(f"✅ Database already has {existing} categories")
        
        session.close()
        
    except Exception as e:
        logger.warning(f"⚠️ Could not insert sample data: {e}")

if __name__ == "__main__":
    main()