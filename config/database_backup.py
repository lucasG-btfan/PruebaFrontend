# config/database_render.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool  # Importar NullPool para Render
import logging

logger = logging.getLogger(__name__)

# ✅ CRÍTICO: Usar la variable de entorno correcta para Render
# En Render, la variable se llama DATABASE_URL (no SQLALCHEMY_DATABASE_URL)
database_url = os.getenv("DATABASE_URL")

# Si DATABASE_URL no existe, usar SQLALCHEMY_DATABASE_URL o un valor por defecto
if not database_url:
    database_url = os.getenv("SQLALCHEMY_DATABASE_URL", "postgresql://user:pass@localhost:5432/dbname")

# ✅ CORREGIR: Postgres en Render usa postgres:// pero SQLAlchemy necesita postgresql://
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

logger.info(f"Database URL configured: {database_url[:50]}...")

# ✅ IMPORTANTE para Render: Usar NullPool para evitar problemas de conexión
engine = create_engine(
    database_url,
    echo=False,  # Cambiar a True solo para debugging local
    poolclass=NullPool,  # ✅ CRÍTICO para Render
    pool_pre_ping=True,  # Verificar conexión antes de usar
    connect_args={
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
            logger.error("❌ CRÍTICO: 'clients' table was NOT created!")

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
