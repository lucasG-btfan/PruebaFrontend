import os
import logging
from sqlalchemy import create_engine, inspect  # Importar inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

logger = logging.getLogger(__name__)

# Obtener la URL de la base de datos
database_url = os.getenv("DATABASE_URL")
if not database_url:
    database_url = os.getenv("SQLALCHEMY_DATABASE_URL", "postgresql://user:pass@localhost:5432/dbname")

# Corregir el formato de la URL para PostgreSQL
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

logger.info(f"Database URL configured: {database_url[:50]}...")

# Configuración del engine para Render
engine = create_engine(
    database_url,
    echo=False,
    poolclass=NullPool,
    pool_pre_ping=True,
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

def initialize_models():
    """
    Placeholder para inicializar modelos.
    En un proyecto real, aquí podrías importar todos los modelos para asegurarte de que estén registrados.
    """
    try:
        # Importar todos los modelos para que SQLAlchemy los registre
        from models import BaseModel  # Asegúrate de que este import funcione
        logger.info("✅ Models initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize models: {e}")
        return False

def create_tables():
    """Create all database tables."""
    try:
        if not initialize_models():
            logger.error("❌ Failed to initialize models")
            return False

        logger.info("🔨 Creating database tables...")
        Base.metadata.create_all(bind=engine)

        # Usar inspect para verificar las tablas creadas
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
