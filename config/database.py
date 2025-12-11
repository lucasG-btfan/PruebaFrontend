import os
import logging
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

logger = logging.getLogger(__name__)

# ✅ Obtener URL de base de datos 
database_url = os.getenv("DATABASE_URL", "").strip()

# Si DATABASE_URL está vacío, usar el valor por defecto
if not database_url:
    logger.warning("⚠️ DATABASE_URL environment variable is empty or not set")
    database_url = "postgresql://ecommerce_db_pg18_user:8wj5MwKBGSfrK3ZG6vADvjT5pkc4ai7u@dpg-d4riokmr433s73a9vb70-a.ohio-postgres.render.com/ecommerce_db_pg18"

# ✅ Corregir protocolo
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

logger.info(f"🔗 Database URL: {database_url[:50]}...")

# ✅ Crear engine
engine = create_engine(
    database_url,
    echo=False,
    poolclass=NullPool,
    pool_pre_ping=True,
    connect_args={
        "sslmode": "require",
        "connect_timeout": 10,
    }
)

# ❌ NO crear nueva Base aquí, importar la tuya
def get_base():
    """Import and return the Base from models."""
    try:
        from models.base_model import Base
        return Base
    except ImportError as e:
        logger.error(f"❌ Failed to import Base: {e}")
        raise

# Obtener Base desde models
Base = get_base()

# Crear sessionmaker con la Base correcta
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

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
        # Importar todos los modelos para que se registren automáticamente
        # El import de __init__.py ya hace esto
        from models import ClientModel, BillModel, OrderModel, OrderDetailModel, ProductModel, CategoryModel, AddressModel, ReviewModel
        
        logger.info("✅ Models imported successfully")
        
        # Verificar que los modelos están registrados
        if hasattr(Base, 'registry') and hasattr(Base.registry, '_class_registry'):
            registered_classes = list(Base.registry._class_registry.keys())
            logger.info(f"📦 Classes registered with Base: {registered_classes}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error initializing models: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def create_tables():
    """Create all database tables."""
    try:
        logger.info("🔨 Creating database tables...")
        
        # Primero asegurarse de que los modelos están importados
        if not initialize_models():
            logger.error("❌ Failed to initialize models")
            return False
        
        # Crear tablas
        Base.metadata.create_all(bind=engine)
        
        # Verificar tablas creadas
        inspector = inspect(engine)
        created_tables = inspector.get_table_names()
        logger.info(f"✅ Tables created successfully: {created_tables}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def check_connection():
    """Check if database is accessible."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            data = result.scalar()
            logger.info(f"✅ Database connection: SUCCESS - {data}")
            
            # Opcional: verificar versión de PostgreSQL
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            logger.info(f"📊 PostgreSQL version: {version[:50]}...")
            
            return True
    except Exception as e:
        logger.error(f"❌ Database connection: FAILED - {str(e)}")
        return False

# Exportar Base también
__all__ = [
    'engine',
    'SessionLocal',
    'get_db',
    'create_tables',
    'check_connection',
    'initialize_models',
    'Base'
]