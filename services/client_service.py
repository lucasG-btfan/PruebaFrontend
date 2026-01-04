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

    def get_all(self, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None):
        try:
            query = self.db.query(ClientModel)
            if is_active is not None:
                query = query.filter(ClientModel.is_active == is_active)
            clients = query.offset(skip).limit(limit).all()
            total = query.count()
            return clients, total
        except Exception as e:
            logger.error(f"Error en get_all: {str(e)}", exc_info=True)
            raise e

    def get_by_id(self, client_id: int) -> Optional[ClientSchema]:
        """Get client by ID."""
        try:
            return self.repository.find(client_id)
        except Exception as e:
            logger.error(f"Error getting client {client_id}: {str(e)}")
            return None
