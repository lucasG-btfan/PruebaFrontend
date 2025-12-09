# repositories/client_repository.py
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.client import ClientModel
from schemas.client_schema import ClientSchema

class ClientRepository:
    def __init__(self, db: Session):
        self.db = db  # ← ESTA LÍNEA ES CRÍTICA
        self.model = ClientModel  
    
    def find_by_email(self, email: str):
        # Asegúrate de usar self.db aquí
        return self.db.query(ClientModel).filter(ClientModel.email == email).first()