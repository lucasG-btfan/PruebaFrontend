# repositories/client_repository.py
from __future__ import annotations
from sqlalchemy.orm import Session
from models.client import ClientModel
from schemas.client_schema import ClientSchema
from repositories.base_repository_impl import BaseRepositoryImpl

class ClientRepository(BaseRepositoryImpl):
    """Repository for Client entity."""

    def __init__(self, db: Session):
        super().__init__(ClientModel, ClientSchema, db)

    def find_by_email(self, email: str):
        """Find client by email."""
        return self.session.query(self.model).filter(
            self.model.email == email
        ).first()
