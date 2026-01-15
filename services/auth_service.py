import hashlib
import hmac
import base64
import secrets
import jwt
from typing import Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from  config.database import get_db
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

class AuthService:
    
    @staticmethod
    def generate_salt() -> str:
        """Generar un salt seguro de 32 bytes en base64"""
        salt_bytes = secrets.token_bytes(32)
        return base64.b64encode(salt_bytes).decode('utf-8')
    
    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        """Hash de contraseña usando PBKDF2-HMAC-SHA256 (SEGURO)"""
        try:
            salt_bytes = base64.b64decode(salt)
        except (ValueError, TypeError):
            salt_bytes = salt.encode('utf-8') if isinstance(salt, str) else salt
        
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt_bytes,
            100000,  
            dklen=32  
        )
        
        return hashed.hex()
    
    @staticmethod
    def verify_password(password: str, salt: str, stored_hash: str) -> bool:
        """Verificar contraseña con compatibilidad hacia atrás"""
        try:
            calculated_hash = AuthService.hash_password(password, salt)
            
            if hmac.compare_digest(calculated_hash, stored_hash):
                return True
                
            old_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return hmac.compare_digest(old_hash, stored_hash)
            
        except Exception as e:
            print(f"Error en verify_password: {e}")
            return False
    
    @staticmethod
    def hash_password_old(password: str, salt: str) -> str:
        """Método antiguo (para compatibilidad con registros existentes)"""
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    # ===== NUEVOS MÉTODOS JWT =====
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crear token JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verificar y decodificar token JWT"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Error de autenticación: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def get_current_client(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ) -> dict:
        """Obtener cliente actual desde el token JWT"""
        from repositories.client_repository import ClientRepository
        
        token = credentials.credentials
        payload = AuthService.verify_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudo validar el token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        client_id = payload.get("client_id")
        if client_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token no contiene client_id",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        client_repo = ClientRepository(db)
        client = client_repo.find(client_id)
        
        if client is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado",
            )
        
        return {
            "id": client.id_key,
            "email": client.email,
            "first_name": client.first_name,
            "last_name": client.last_name,
            "phone": client.phone,
            "is_admin": client.id_key == 0  
        }