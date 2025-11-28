import os
import redis
import logging

logger = logging.getLogger(__name__)

# Check if we're in Render
RENDER = os.getenv('RENDER', 'false').lower() == 'true'

if RENDER:
    # En Render, no usar Redis (problemas de DNS)
    redis_client = None
    redis_config = None  # ← Mantener compatibilidad
    logger.info("🚫 Redis disabled on Render due to DNS issues")
else:
    # En desarrollo, intentar conectar a Redis
    try:
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        redis_db = int(os.getenv('REDIS_DB', 0))
        
        redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True
        )
        redis_config = redis_client  # ← Mantener compatibilidad
        # Test connection
        redis_client.ping()
        logger.info("✅ Redis connected successfully")
    except Exception as e:
        logger.warning(f"⚠️ Redis connection failed: {e}")
        redis_client = None
        redis_config = None
        logger.info("Application will run without caching")

def check_redis_connection():
    """Check Redis connection"""
    if redis_client is None:
        return False
    try:
        return redis_client.ping()
    except Exception:
        return False

def close():
    """Close Redis connection"""
    if redis_client:
        redis_client.close()