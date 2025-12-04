"""
Simple constants for production.
"""
import os

# Application metadata
APP_NAME = "E-commerce API"
APP_DESCRIPTION = "E-commerce REST API"
APP_VERSION = "1.0.0"

# Server configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "10000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# CORS configuration
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# API settings
ENABLE_DOCS = os.getenv("ENABLE_DOCS", "True").lower() == "true"