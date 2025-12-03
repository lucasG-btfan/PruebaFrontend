# config/__init__.py
"""
Configuration package initialization.
Exports database components for easy import.
"""

from config.database_render import (
    engine,
    SessionLocal,
    get_db,
    create_tables,
    check_connection
)