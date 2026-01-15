import hashlib
import hmac
import base64
import secrets
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from config.database import get_db
import logging

logger = logging.getLogger(__name__)
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
            logger.error(f"Error en verify_password: {e}")
            return False
    
    @staticmethod
    def hash_password_old(password: str, salt: str) -> str:
        """Método antiguo (para compatibilidad con registros existentes)"""
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    @staticmethod
    def get_current_client(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ) -> dict:
        """Obtener cliente actual desde el token JWT"""
        from jose import jwt
        import os
        from repositories.client_repository import ClientRepository
        
        try:
            SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
            ALGORITHM = "HS256"
            
            token = credentials.credentials
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            client_id_str = payload.get("sub")
            
            if client_id_str is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token no contiene client_id (sub)"
                )
            
            client_id = int(client_id_str)
            
            # Obtener cliente de la base de datos
            client_repo = ClientRepository(db)
            client = client_repo.find(client_id)
            
            if client is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente no encontrado"
                )
            
            # Convertir a diccionario para el frontend
            return {
                "id": client.id_key,
                "email": client.email,
                "first_name": client.name,  # Cambié de first_name a name para coincidir con tu modelo
                "last_name": client.lastname,  # Cambié de last_name a lastname
                "phone": client.phone,
                "is_admin": client.id_key == 0
            }
            
        except jwt.JWTError as e:
            logger.error(f"Error JWT: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado"
            )
        except ValueError as e:
            logger.error(f"Error convirtiendo ID: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token mal formado"
            )
        except Exception as e:
            logger.error(f"Error inesperado en get_current_client: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )
    
    @staticmethod
    def get_current_client_simple(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> dict:
        """Versión simple que solo decodifica el token sin verificar en BD"""
        from jose import jwt
        import os
        
        try:
            SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
            ALGORITHM = "HS256"
            
            token = credentials.credentials
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            client_id_str = payload.get("sub")
            
            if client_id_str is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token no contiene client_id (sub)"
                )
            
            client_id = int(client_id_str)
            
            # NOTA: Esta versión NO verifica en la base de datos
            return {
                "id": client_id,
                "email": payload.get("email", ""),
                "is_admin": client_id == 0
            }
            
        except jwt.JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Error de autenticación: {str(e)}"
            )