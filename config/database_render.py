import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)

# Determinar si estamos en Render (usar SQLite) o desarrollo (usar PostgreSQL)
RENDER = os.getenv('RENDER', 'false').lower() == 'true'

if RENDER:
    # En Render, usar SQLite
    DATABASE_URL = "sqlite:///./render_app.db"
    logger.info("🚀 Using SQLite database on Render")
else:
    # En desarrollo, usar PostgreSQL de ElephantSQL
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        logger.error("❌ DATABASE_URL not set for development")
        DATABASE_URL = "sqlite:///./dev_fallback.db"
    
    # Fix URL format for PostgreSQL
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    logger.info("🔧 Using PostgreSQL database")

logger.info(f"Database URL: {DATABASE_URL}")

# Create engine
try:
    if RENDER or DATABASE_URL.startswith('sqlite'):
        # SQLite configuration
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False}
        )
    else:
        # PostgreSQL configuration
        engine = create_engine(
            DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True
        )
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("✅ Database engine created successfully")
    
except Exception as e:
    logger.error(f"❌ Failed to create database engine: {e}")
    # Fallback to SQLite
    DATABASE_URL = "sqlite:///./fallback.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("🔄 Using fallback SQLite database")

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)
    
def check_connection():
    """Check if database is accessible"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        logger.info("✅ Database connection check: SUCCESS")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection check: FAILED - {str(e)}")
        return False