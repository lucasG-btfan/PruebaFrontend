
import hashlib
import os
import base64
from datetime import datetime, timedelta
from typing import Optional

class AuthService:
    @staticmethod
    def generate_salt():
        return base64.b64encode(os.urandom(32)).decode('utf-8')
    
    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        """Hash password with salt using SHA-256."""
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, salt: str, stored_hash: str) -> bool:
        """Verify password against stored hash."""
        return AuthService.hash_password(password, salt) == stored_hash