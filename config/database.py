# config/database.py
"""
Database configuration wrapper for Render.
This file redirects imports to database_render.py for compatibility.
"""
import sys
import os

print("🔄 Redirigiendo imports a database_render.py...")

# Importar todo desde database_render
from .database_render import *

# Para compatibilidad con alembic y otros archivos
DATABASE_URI = os.getenv("DATABASE_URL", "")

# Si no está definido, usar la de database_render
if not DATABASE_URI and 'DATABASE_URL' in globals():
    DATABASE_URI = DATABASE_URL

# Si todavía no está definido, usar la variable local
if not DATABASE_URI:
    DATABASE_URI = "postgresql://ecommerce_user:XuchJ7YFaWcfTnq4s1RX4CpTTGrxwfbG@dpg-d4mvsm1r0fns73ai8s10-a.ohio-postgres.render.com/ecommerce_db_sbeb"

print(f"✅ Database config loaded: {DATABASE_URI[:50]}...")

__all__ = [
    'engine',
    'SessionLocal',
    'get_db',
    'create_tables',
    'check_connection',
    'initialize_models',
    'DATABASE_URI',
    'DATABASE_URL'
]