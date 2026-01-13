import hashlib
import hmac
import base64
import secrets
from typing import Optional, Tuple

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