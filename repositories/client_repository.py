from __future__ import annotations
from sqlalchemy.orm import Session
from models.client import ClientModel
from schemas.client_schema import ClientSchema
from repositories.base_repository_impl import BaseRepositoryImpl

class ClientRepository(BaseRepositoryImpl):
    """Repository for Client entity."""

    def __init__(self, db: Session):
        super().__init__(ClientModel, ClientSchema, db)

    def get_by_id(self, id: int):
        """Get client by ID."""
        return self.db.query(self.model).filter(self.model.id_key == id).first()

    def find_by_email(self, email: str):
        """Find client by email."""
        return self.db.query(self.model).filter(self.model.email == email).first()

    def search_by_name(self, name: str):
        """Search clients by name (partial match)."""
        return self.db.query(self.model).filter(
            self.model.name.ilike(f"%{name}%")
        ).all()
