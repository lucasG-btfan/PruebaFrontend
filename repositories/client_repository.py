# repositories/client_repository.py
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.client import ClientModel
from schemas.client_schema import ClientSchema

class ClientRepository:
    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db
        self.model = ClientModel  # Añade esta línea si usas un modelo

    def find_by_email(self, email: str) -> Optional[ClientModel]:
        """Find a client by email."""
        if not hasattr(self, 'db') or self.db is None:
            raise AttributeError("Database session (db) not initialized")
        
        try:
            return self.db.query(ClientModel).filter(ClientModel.email == email).first()
        except Exception as e:
            print(f"Error in find_by_email: {str(e)}")
            return None

    def save(self, client_data: dict) -> ClientModel:
        """Save a new client to database."""
        try:
            # Crear instancia del modelo
            client = ClientModel(**client_data)
            
            # Guardar en la base de datos
            self.db.add(client)
            self.db.commit()
            self.db.refresh(client)
            
            return client
        except Exception as e:
            self.db.rollback()
            print(f"Error saving client: {str(e)}")
            raise

    def find(self, client_id: int) -> Optional[ClientModel]:
        """Find client by ID."""
        try:
            return self.db.query(ClientModel).filter(ClientModel.id == client_id).first()
        except Exception as e:
            print(f"Error finding client {client_id}: {str(e)}")
            return None

    def find_all(self, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None) -> Tuple[List[ClientModel], int]:
        """Find all clients with pagination."""
        try:
            query = self.db.query(ClientModel)
            
            # Filtrar por estado activo si se especifica
            if is_active is not None:
                query = query.filter(ClientModel.is_active == is_active)
            
            # Contar total
            total = query.count()
            
            # Aplicar paginación
            clients = query.order_by(desc(ClientModel.created_at)).offset(skip).limit(limit).all()
            
            return clients, total
        except Exception as e:
            print(f"Error finding all clients: {str(e)}")
            return [], 0

    def update(self, client_id: int, client_data: dict) -> Optional[ClientModel]:
        """Update an existing client."""
        try:
            client = self.find(client_id)
            if not client:
                return None
            
            # Actualizar campos
            for key, value in client_data.items():
                if hasattr(client, key) and value is not None:
                    setattr(client, key, value)
            
            self.db.commit()
            self.db.refresh(client)
            return client
        except Exception as e:
            self.db.rollback()
            print(f"Error updating client {client_id}: {str(e)}")
            return None

    def delete(self, client_id: int) -> bool:
        """Soft delete a client."""
        try:
            client = self.find(client_id)
            if not client:
                return False
            
            # Soft delete (marcar como inactivo)
            client.is_active = False
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error deleting client {client_id}: {str(e)}")
            return False