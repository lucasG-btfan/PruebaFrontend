import os
import sys
import logging
import traceback
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

print("🔧 Cargando configuración de base de datos...")

logger = logging.getLogger(__name__)

try:
    # Importar la base de modelos
    from models.base_model import base as Base

    # Obtener la URL de la base de datos desde variables de entorno
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ecommerce_user:XuchJ7YFaWcfTnq4s1RX4CpTTGrxwfbG@dpg-d4mvsm1r0fns73ai8s10-a.ohio-postgres.render.com/ecommerce_db_sbeb")

    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL no está definido")
        sys.exit(1)

    # Asegúrate de que la URL comience con postgresql:// (no postgres://)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    logger.info(f"🚀 Using PostgreSQL database: {DATABASE_URL.split('@')[0]}...")

    # Configuración optimizada para Render
    engine = create_engine(
        DATABASE_URL,
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

    def get_db():
        """Dependency for getting database session."""
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def initialize_models():
        """Initialize and import all models to ensure they are registered with Base."""
        logger.info("📦 Initializing SQLAlchemy models...")
        try:
            from models.client import ClientModel
            logger.info(f"✅ ClientModel registered: {hasattr(ClientModel, '__tablename__')}")
            return True
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
                logger.error("❌ CRÍTICO: 'clients' table was NOT created!")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create database tables: {e}")
            return False

    def check_connection():
        """Check if database is accessible"""
        try:
            with engine.connect() as conn:
                # Usa text() para SQL crudo
                conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection check: SUCCESS")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection check: FAILED - {str(e)}")
            return False

except Exception as e:
    print(f"❌ Error en database_render.py: {e}")
    traceback.print_exc()
    sys.exit(1)
