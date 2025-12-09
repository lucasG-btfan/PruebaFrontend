# services/client_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging
from typing import Optional, Tuple, List
from models.client import ClientModel
from repositories.client_repository import ClientRepository
from schemas.client_schema import ClientSchema, ClientCreateSchema
from services.base_service_impl import BaseServiceImpl

logger = logging.getLogger(__name__)

class ClientService(BaseServiceImpl):
    def __init__(self, db: Session):
        super().__init__(
            repository_class=ClientRepository,
            model=ClientModel,
            schema=ClientSchema,
            db=db
        )

    def create(self, client_data: ClientCreateSchema):
        """Create a new client with email validation"""
        try:
            logger.info(f"Creating client: {client_data.email}")

            # Check if email already exists
            existing_client = self.repository.find_by_email(client_data.email)
            if existing_client:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email {client_data.email} already registered"
                )

            # Call the parent save method
            return self.save(client_data)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating client: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating client: {str(e)}"
            )

    def get_all(self, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None) -> Tuple[List[ClientSchema], int]:
        """Get all clients with pagination and optional active filter"""
        try:
            return self.repository.find_all(skip=skip, limit=limit, is_active=is_active)
        except Exception as e:
            logger.error(f"Error getting clients: {str(e)}")
            return [], 0

    def get_by_id(self, client_id: int) -> ClientSchema:
        """Get client by ID"""
        try:
            return self.repository.find(client_id)
        except Exception as e:
            logger.error(f"Error getting client {client_id}: {str(e)}")
            return None
