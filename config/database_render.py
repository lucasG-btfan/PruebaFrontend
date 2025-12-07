import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import logging

logger = logging.getLogger(__name__)

try:
    from models.base_model import Base
    from models.client import ClientModel
    from models.bill import BillModel
    from models.order import OrderModel
    from models.order_detail import OrderDetailModel
    from models.product import ProductModel
    from models.category import CategoryModel
    from models.address import AddressModel
    from models.review import ReviewModel
    
    models_imported = True
    logger.info("✅ Models imported successfully")
except ImportError as e:
    models_imported = False
    logger.warning(f"⚠️ Could not import models: {e}")

# ✅ Obtener URL de base de datos - CORREGIR ESTO
database_url = os.getenv("DATABASE_URL", "").strip()

# Si DATABASE_URL está vacío, usar el valor por defecto
if not database_url:
    logger.warning("⚠️ DATABASE_URL environment variable is empty or not set")
    # Usar la URL directa como fallback
    database_url = "postgresql://ecommerce_user:XuchJ7YFaWcfTnq4s1RX4CpTTGrxwfbG@dpg-d4mvsm1r0fns73ai8s10-a.ohio-postgres.render.com/ecommerce_db_sbeb"
    logger.info("📝 Using default database URL")

# ✅ CORREGIR: Postgres en Render usa postgres:// pero SQLAlchemy necesita postgresql://
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
    logger.info("🔄 Fixed database URL protocol")

logger.info(f"🔗 Database URL: {database_url[:50]}...")

# ✅ Crear engine CON SSL - ESTO ES CLAVE
engine = create_engine(
    database_url,
    echo=False,  # Cambiar a True solo para debugging
    poolclass=NullPool,  # ✅ Para Render
    pool_pre_ping=True,
    connect_args={
        "sslmode": "require",  # ✅ SSL REQUERIDO para Render
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def initialize_models():
    """Initialize all models to ensure they're registered with Base."""
    try:
        if not models_imported:
            logger.error("❌ Models were not imported correctly")
            return False

        # Verificar que Base tenga metadata
        if hasattr(Base, 'metadata') and hasattr(Base.metadata, 'tables'):
            logger.info(f"✅ Models initialized. Tables registered: {list(Base.metadata.tables.keys())}")
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

        if 'clients' in created_tables:
            columns = inspector.get_columns('clients')
            logger.info("📋 Structure of 'clients' table:")
            for col in columns:
                logger.info(f"   - {col['name']}: {col['type']}")
        else:
            logger.warning("⚠️ 'clients' table was NOT created!")

        return True
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        return False

def check_connection():
    """Check if database is accessible"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("✅ Database connection check: SUCCESS")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection check: FAILED - {str(e)}")
        return False

# ✅ Crear Base si no se importó de los modelos (no debería ser necesario si Base está en base_model.py)
if not models_imported:
    Base = declarative_base()
    logger.warning("⚠️ Using declarative_base() because models were not imported")
