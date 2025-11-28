import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    logger.error("❌ DATABASE_URL environment variable is not set!")
    # En producción, esto debería fallar
    raise ValueError("DATABASE_URL environment variable is required")

# Fix URL format
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

logger.info(f"🔧 Database URL: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else 'local'}")

try:
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
    raise

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
        # Try a simple query
        result = db.execute("SELECT 1 as test")
        db.close()
        logger.info("✅ Database connection check: SUCCESS")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection check: FAILED - {str(e)}")
        return False