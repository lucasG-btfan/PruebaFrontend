import os
import logging
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

logger = logging.getLogger(__name__)
database_url = os.getenv("DATABASE_URL", "").strip()

if not database_url:
    logger.warning("⚠️ DATABASE_URL no está configurada. Usando valor por defecto para desarrollo local.")
    database_url = "postgresql://postgres:postgres@localhost:5432/ecommerce_db"

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

logger.info(f"🔗 Conectando a la base de datos: {database_url[:50]}...")

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

Base = declarative_base()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    """Dependency para obtener una sesión de la base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def initialize_models():
    """Importar todos los modelos para registrarlos con Base."""
    try:
        from models import (
            ClientModel, BillModel, OrderModel, OrderDetailModel,
            ProductModel, CategoryModel, AddressModel, ReviewModel
        )
        logger.info("✅ Modelos importados correctamente")

        # Verificar que los modelos están registrados
        if hasattr(Base, 'registry') and hasattr(Base.registry, '_class_registry'):
            registered_classes = list(Base.registry._class_registry.keys())
            logger.info(f"📦 Clases registradas con Base: {registered_classes}")

        return True
    except Exception as e:
        logger.error(f"❌ Error al inicializar modelos: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def create_tables():
    """Crear todas las tablas de la base de datos."""
    try:
        logger.info("🔨 Creando tablas en la base de datos...")

        if not initialize_models():
            logger.error("❌ Falló la inicialización de modelos")
            return False

        Base.metadata.create_all(bind=engine)

        inspector = inspect(engine)
        created_tables = inspector.get_table_names()
        logger.info(f"✅ Tablas creadas correctamente: {created_tables}")

        return True
    except Exception as e:
        logger.error(f"❌ Falló la creación de tablas: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def check_connection():
    """Verificar si la base de datos es accesible."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            data = result.scalar()
            logger.info(f"✅ Conexión a la base de datos: ÉXITO - {data}")

            # Opcional: verificar versión de PostgreSQL
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            logger.info(f"📊 Versión de PostgreSQL: {version[:50]}...")

            return True
    except Exception as e:
        logger.error(f"❌ Conexión a la base de datos: FALLIDA - {str(e)}")
        return False

__all__ = [
    'engine',
    'SessionLocal',
    'get_db',
    'create_tables',
    'check_connection',
    'initialize_models',
    'Base'
]
