import hashlib
import hmac
import base64
import secrets
from typing import Tuple

class AuthService:
    
    @staticmethod
    def generate_salt() -> str:
        """Generar un salt seguro de 32 bytes en base64"""
        salt_bytes = secrets.token_bytes(32)
        return base64.b64encode(salt_bytes).decode('utf-8')
    
    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        """Hash de contraseña usando PBKDF2-HMAC-SHA256 (seguro)"""
        try:
            salt_bytes = base64.b64decode(salt)
        except Exception:
            salt_bytes = salt.encode('utf-8')
        
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
        """Verificar contraseña de manera segura"""
        try:
            calculated_hash = AuthService.hash_password(password, salt)
            
            return hmac.compare_digest(calculated_hash, stored_hash)
        except Exception:
            # Si falla PBKDF2, probar el método antiguo (backward compatibility)
            old_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return hmac.compare_digest(old_hash, stored_hash)
    
    @staticmethod
    def migrate_old_hash(password: str, old_salt: str, old_hash: str) -> Tuple[str, str]:
        """Migrar hash antiguo a nuevo sistema"""
        # Generar nuevo salt
        new_salt = AuthService.generate_salt()
        
        # Crear nuevo hash con PBKDF2
        new_hash = AuthService.hash_password(password, new_salt)
        
        return new_salt, new_hash