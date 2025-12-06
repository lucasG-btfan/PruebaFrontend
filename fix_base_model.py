# fix_base_model.py
import os

# Asegurarse de que el directorio 'models' exista
os.makedirs("models", exist_ok=True)

# Ruta del archivo base_model.py
base_model_path = "models/base_model.py"

# Contenido corregido y completo
new_content = '''from sqlalchemy import Integer, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
import datetime

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass

class BaseModel(Base):
    """Abstract base model with common fields."""
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False
    )

    @declared_attr
    def __tablename__(cls):
        """Generate table name from class name."""
        return cls.__name__.replace('Model', '').lower() + 's'

    def to_dict(self):
        """Convert model instance to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
'''

# Escribir el archivo corregido
with open(base_model_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ models/base_model.py corregido")
