# services/client_service.py
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging
from models.client import ClientModel
from schemas.client_schema import ClientSchema, ClientCreateSchema
from repositories.client_repository import ClientRepository

logger = logging.getLogger(__name__)

class ClientService:
    def __init__(self, db: Session):
        self.repository = ClientRepository(db)

    def create(self, client_data: ClientCreateSchema) -> ClientModel:
        """Create a new client with email validation."""
        logger.info(f"Creating client: {client_data.email}")

        # Check if email already exists
        existing_client = self.repository.find_by_email(client_data.email)
        if existing_client:
            raise ValueError(f"Client with email {client_data.email} already exists")

        # Create the client
        client_dict = client_data.dict()
        return self.repository.save(client_dict)

    def get_all(self, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None) -> Tuple[List[ClientSchema], int]:
        """Get all clients with pagination and optional active filter."""
        try:
            return self.repository.find_all(skip=skip, limit=limit, is_active=is_active)
        except Exception as e:
            logger.error(f"Error getting clients: {str(e)}")
            return [], 0

    def get_by_id(self, client_id: int) -> Optional[ClientSchema]:
        """Get client by ID."""
        try:
            return self.repository.find(client_id)
        except Exception as e:
            logger.error(f"Error getting client {client_id}: {str(e)}")
            return None
