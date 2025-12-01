import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool  # Importante para Render
import logging

logger = logging.getLogger(__name__)

# ✅ Construir la URL de PostgreSQL a partir de las variables de entorno
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "dpg-d4mvsm1r0fns73ai8s10-a")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "ecommerce_db_sbeb")
POSTGRES_USER = os.getenv("POSTGRES_USER", "ecommerce_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "XuchJ7YFaWcfTnq4s1RX4CpTTGrxwfbG")

# ✅ Construir la URL de conexión a PostgreSQL
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

logger.info(f"🚀 Using PostgreSQL database: {POSTGRES_USER}@{POSTGRES_HOST}...")

try:
    # ✅ Configuración optimizada para Render
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # Cambiar a True solo para debugging local
        poolclass=NullPool,  # ✅ CRÍTICO para Render
        pool_pre_ping=True,  # Verificar conexión antes de usarla
        connect_args={
            "connect_timeout": 10,
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5,
        }
    )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("✅ PostgreSQL database engine created successfully")

except Exception as e:
    logger.error(f"❌ Failed to create database engine: {e}")
    # ✅ En caso de error, usar SQLite como respaldo (opcional)
    DATABASE_URL = "sqlite:///./fallback.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("🔄 Using emergency SQLite database")

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
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        raise

def check_connection():
    """Check if database is accessible"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection check: SUCCESS")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection check: FAILED - {str(e)}")
        return False
