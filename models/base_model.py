# models/base_model.py
"""
Base model for all database models.
Provides common columns and methods.
"""
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr

# Use a consistent naming convention
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Create metadata with naming convention
metadata = MetaData(naming_convention=convention)

# Create base class
base = declarative_base(metadata=metadata)


class BaseModel(base):
    """
    Abstract base model with common columns.
    All models should inherit from this.
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @declared_attr
    def __tablename__(cls):
        """Generate table name from class name."""
        return cls.__name__.replace('Model', '').lower() + 's'

    def to_dict(self):
        """Convert model instance to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}