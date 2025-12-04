"""
Configuration package initialization.
Exports database components and application constants for easy import.
"""
# Import constants
from config.constants import (
    APP_NAME,
    APP_DESCRIPTION,
    APP_VERSION,
    HOST,
    PORT,
    DEBUG,
    DATABASE_URL,
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB,
    ALLOWED_ORIGINS,
    ENABLE_DOCS,
    LOG_LEVEL,
    LOG_FILE,
    ERROR_LOG_FILE,
    RATE_LIMIT_ENABLED,
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_PERIOD,
    CACHE_TTL,
    PaginationConfig,
    CacheConfig,
    LogConfig,
    RateLimitConfig,
    DatabaseConfig,
    ValidationConfig,
    ErrorMessages
)

# Import database components
from config.database_render import (
    engine,
    SessionLocal,
    get_db,
    create_tables,
    check_connection
)

# List of exports
__all__ = [
    # Constants
    'APP_NAME',
    'APP_DESCRIPTION',
    'APP_VERSION',
    'HOST',
    'PORT',
    'DEBUG',
    'DATABASE_URL',
    'REDIS_HOST',
    'REDIS_PORT',
    'REDIS_DB',
    'ALLOWED_ORIGINS',
    'ENABLE_DOCS',
    'LOG_LEVEL',
    'LOG_FILE',
    'ERROR_LOG_FILE',
    'RATE_LIMIT_ENABLED',
    'RATE_LIMIT_REQUESTS',
    'RATE_LIMIT_PERIOD',
    'CACHE_TTL',
    'PaginationConfig',
    'CacheConfig',
    'LogConfig',
    'RateLimitConfig',
    'DatabaseConfig',
    'ValidationConfig',
    'ErrorMessages',
    # Database components
    'engine',
    'SessionLocal',
    'get_db',
    'create_tables',
    'check_connection'
]
