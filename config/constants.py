"""
Application Constants - Versión específica para Render
Centralized configuration constants for the entire application.
Optimized for production deployment on Render.
"""
import os
from typing import List

# Application metadata
APP_NAME = os.getenv("APP_NAME", "E-commerce REST API")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "E-commerce REST API")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

# Server configuration - CRÍTICO PARA RENDER
HOST = "0.0.0.0"  # Siempre esto en Render
PORT = int(os.getenv("PORT", "10000"))  # Render proporciona PORT automáticamente

# Debug - DESACTIVADO en producción
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Redis configuration (si usas Redis en Render)
REDIS_HOST = os.getenv("REDIS_HOST", "")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# CORS configuration - PROCESAR CORRECTAMENTE LA CADENA DE RENDER
cors_origins_str = os.getenv("CORS_ORIGINS", "")
ALLOWED_ORIGINS = []
if cors_origins_str:
    # Separar por comas y limpiar espacios
    ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins_str.split(",")]
    print(f"✅ CORS origins loaded: {ALLOWED_ORIGINS}")
else:
    # Fallback a orígenes comunes
    ALLOWED_ORIGINS = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://pruebafrontend-ea20.onrender.com"
    ]
    print("⚠️ CORS_ORIGINS not set, using defaults")

# También agregar el propio dominio de Render si está disponible
render_url = os.getenv("RENDER_EXTERNAL_URL", "")
if render_url and render_url not in ALLOWED_ORIGINS:
    ALLOWED_ORIGINS.append(render_url)

# API settings
ENABLE_DOCS = os.getenv("ENABLE_DOCS", "true").lower() == "true"
API_V1_PREFIX = "/api/v1"
PROJECT_NAME = "E-commerce API"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "logs/app.log"
ERROR_LOG_FILE = "logs/error.log"

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Rate limiting
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "60"))  # seconds

# Database connection constants
class DatabaseConfig:
    """Database connection constants"""
    DEFAULT_POOL_SIZE = 50
    DEFAULT_MAX_OVERFLOW = 100
    DEFAULT_POOL_TIMEOUT = 10  # seconds (fail fast for high concurrency)
    DEFAULT_POOL_RECYCLE = 3600  # 1 hour

# Pagination-related constants
class PaginationConfig:
    """Pagination-related constants"""
    DEFAULT_SKIP = 0
    DEFAULT_LIMIT = 100
    MAX_LIMIT = int(os.getenv('PAGINATION_MAX_LIMIT', '1000'))
    MIN_LIMIT = 1

# Cache TTL and configuration constants
class CacheConfig:
    """Cache TTL and configuration constants"""
    # Default TTLs in seconds
    DEFAULT_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes
    PRODUCT_LIST_TTL = 300  # 5 minutes
    PRODUCT_ITEM_TTL = 300  # 5 minutes
    CATEGORY_LIST_TTL = 3600  # 1 hour (rarely changes)
    CATEGORY_ITEM_TTL = 3600  # 1 hour

# Validation-related constants
class ValidationConfig:
    """Validation-related constants"""
    # Price validation
    MIN_PRICE = 0.01  # Minimum price (must be positive)
    MAX_PRICE = 999999.99  # Maximum reasonable price
    # Stock validation
    MIN_STOCK = 0  # Minimum stock (non-negative)
    MAX_STOCK = 999999  # Maximum reasonable stock
    # String length limits
    MIN_NAME_LENGTH = 1
    MAX_NAME_LENGTH = 200
    MAX_DESCRIPTION_LENGTH = 2000
    MAX_EMAIL_LENGTH = 255
    # Phone validation
    PHONE_REGEX = r'^\+?[1-9]\d{6,19}$'  # International format
    # Price comparison precision
    PRICE_EPSILON = 0.01  # For float comparison

# Centralized error message templates
class ErrorMessages:
    """Centralized error message templates"""
    INSTANCE_NOT_FOUND = "{resource} with ID {id} not found"
    INSUFFICIENT_STOCK = "Insufficient stock for product {product_id}: requested {requested}, available {available}"
    PRICE_MISMATCH = "Price mismatch for product {product_id}: expected {expected}, got {actual}"
    INVALID_PAGINATION = "Invalid pagination: skip must be >= 0 and limit must be between {min} and {max}"
    PROTECTED_FIELD = "Cannot update protected field: {field}"
    INVALID_FIELD = "Invalid field for {model}: {field}"
    RATE_LIMIT_EXCEEDED = "Rate limit exceeded. Maximum {limit} requests per {period} seconds"

# Imprimir configuración cargada
print(f"🚀 Configuration loaded:")
print(f"  • Port: {PORT}")
print(f"  • CORS Origins: {ALLOWED_ORIGINS}")
print(f"  • Database URL set: {bool(DATABASE_URL)}")
print(f"  • Docs enabled: {ENABLE_DOCS}")
