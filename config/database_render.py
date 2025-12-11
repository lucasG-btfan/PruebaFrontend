# config/database.py - ÚNICO archivo de configuración de DB
import os
import logging
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

logger = logging.getLogger(__name__)

# ✅ Obtener URL de base de datos 
database_url = os.getenv("DATABASE_URL", "").strip()

# Si DATABASE_URL está vacío, usar el valor por defecto
if not database_url:
    logger.warning("⚠️ DATABASE_URL environment variable is empty or not set")
    # Usar la URL directa como fallback
    database_url = "postgresql://ecommerce_db_pg18_user:8wj5MwKBGSfrK3ZG6vADvjT5pkc4ai7u@dpg-d4riokmr433s73a9vb70-a.ohio-postgres.render.com/ecommerce_db_pg18"

# ✅ CORREGIR: Postgres en Render usa postgres:// pero SQLAlchemy necesita postgresql://
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

logger.info(f"🔗 Database URL: {database_url[:50]}...")

# ✅ Crear engine CON SSL - ESTO ES CLAVE para Render
engine = create_engine(
    database_url,
    echo=False,
    poolclass=NullPool,  # ✅ Para Render
    pool_pre_ping=True,
    connect_args={
        "sslmode": "require",  # ✅ SSL REQUERIDO para Render
        "connect_timeout": 10,
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ Crear Base FIRST
Base = declarative_base()

def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def initialize_models():
    """Import all models to register them with Base."""
    try:
        # Importar todos los modelos para que se registren con Base
        from models.base_model import Base as ModelsBase
        from models.client import ClientModel
        from models.bill import BillModel
        from models.order import OrderModel
        from models.order_detail import OrderDetailModel
        from models.product import ProductModel
        from models.category import CategoryModel
        from models.address import AddressModel
        from models.review import ReviewModel
        
        logger.info("✅ Models imported successfully")
        
        # Usar el mismo Base de models
        global Base
        Base = ModelsBase
        
        if hasattr(Base, 'metadata') and hasattr(Base.metadata, 'tables'):
            logger.info(f"📦 Tables registered: {list(Base.metadata.tables.keys())}")
            return True
        else:
            logger.error("❌ Base metadata not properly configured")
            return False
    except Exception as e:
        logger.error(f"❌ Error initializing models: {e}")
        return False

def create_tables():
    """Create all database tables."""
    try:
        if not initialize_models():
            logger.error("❌ Failed to initialize models")
            return False

        logger.info("🔨 Creating database tables...")
        Base.metadata.create_all(bind=engine)

        inspector = inspect(engine)
        created_tables = inspector.get_table_names()
        logger.info(f"✅ Tables created successfully: {created_tables}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        return False

def check_connection():
    """Check if database is accessible"""
    try:
        with engine.connect() as conn:
            # ✅ IMPORTANTE: Usar text() para crear un statement SQL ejecutable
            result = conn.execute(text("SELECT 1"))
            data = result.scalar()
            logger.info(f"✅ Database connection check: SUCCESS - {data}")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection check: FAILED - {str(e)}")
        return False