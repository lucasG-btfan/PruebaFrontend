from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from config.database import get_db
from schemas.client_schema import ClientLoginSchema, ClientRegisterSchema, DebugPasswordSchema
from models.client import ClientModel
from services.auth_service import AuthService
from jose import jwt
from middleware.auth_middleware import get_current_user
import os
import logging
import hashlib  
import base64   
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Authentication"])  

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

def create_access_token(data: dict) -> str:
    """Crea un token JWT con los datos proporcionados."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user_id_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Obtiene el ID del cliente desde el token JWT."""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        client_id_str = payload.get("sub")

        if client_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales de autenticación inválidas"
            )

        return int(client_id_str)

    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de autenticación inválidas"
        )

@router.post("/login", summary="Iniciar sesión", response_description="Retorna el token de acceso y datos del cliente")
async def login(login_data: ClientLoginSchema, db: Session = Depends(get_db)):
    """Endpoint para iniciar sesión."""
    logger.info(f"Intento de inicio de sesión para: {login_data.email}")

    client = db.query(ClientModel).filter(
        ClientModel.email == login_data.email,
        ClientModel.is_active == True
    ).first()

    if not client:
        logger.warning(f"Cliente no encontrado o inactivo: {login_data.email}")
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Verificar contraseña
    is_valid = AuthService.verify_password(
        login_data.password.get_secret_value(),
        client.password_salt,
        client.password_hash
    )

    if not is_valid:
        logger.warning(f"Contraseña inválida para: {login_data.email}")
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Crear token
    access_token = create_access_token(data={"sub": str(client.id_key)})

    logger.info(f"Inicio de sesión exitoso para: {login_data.email}")
    return {
        "message": "Inicio de sesión exitoso",
        "access_token": access_token,
        "token_type": "bearer",
        "client": {
            "id": client.id_key,
            "email": client.email,
            "name": f"{client.name} {client.lastname}",
            "is_admin": client.id_key == 0
        }
    }

@router.post("/register", summary="Registrar cliente", response_description="Retorna el token de acceso y datos del nuevo cliente")
async def register(register_data: ClientRegisterSchema, db: Session = Depends(get_db)):
    """Endpoint para registrar un nuevo cliente."""
    logger.info(f"Intento de registro para: {register_data.email}")

    existing = db.query(ClientModel).filter(ClientModel.email == register_data.email).first()
    if existing:
        logger.warning(f"Email ya registrado: {register_data.email}")
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    if register_data.password.get_secret_value() != register_data.confirm_password.get_secret_value():
        logger.warning(f"Las contraseñas no coinciden para: {register_data.email}")
        raise HTTPException(status_code=400, detail="Las contraseñas no coinciden")

    salt = AuthService.generate_salt()
    password_hash = AuthService.hash_password(
        register_data.password.get_secret_value(),
        salt
    )

    # Crear cliente
    client_data = register_data.dict(exclude={'password', 'confirm_password', 'id_key'})
    client = ClientModel(
        **client_data,
        password_hash=password_hash,
        password_salt=salt,
        is_active=True
    )

    db.add(client)
    try:
        db.commit()
        db.refresh(client)
        logger.info(f"Registro exitoso para: {register_data.email}, ID: {client.id_key}")

        access_token = create_access_token(data={"sub": str(client.id_key)})
        return {
            "message": "Registro exitoso",
            "client": {
                "id": client.id_key,
                "email": client.email,
                "name": f"{client.name} {client.lastname}",
                "is_admin": False
            },
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error durante el registro: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/verify", summary="Verificar token", response_description="Retorna si el token es válido")
async def verify_token(current_user_id_key: int = Depends(get_current_user_id_key)):
    """Verifica que el token JWT sea válido."""
    return {
        "valid": True,
        "client_id": current_user_id_key,
        "message": "Token válido"
    }

@router.get("/me", summary="Obtener perfil", response_description="Retorna los datos del cliente actual")
async def get_me(current_user: ClientModel = Depends(get_current_user)):
    """Obtiene la información del cliente autenticado."""
    return {
        "id": current_user.id_key,
        "email": current_user.email,
        "name": f"{current_user.name} {current_user.lastname}",
        "is_admin": current_user.id_key == 0
    }

@router.post("/debug-password", include_in_schema=False)
async def debug_password(debug_data: DebugPasswordSchema, db: Session = Depends(get_db)):
    """Endpoint de diagnóstico para contraseñas (solo para desarrollo)."""
    client = db.query(ClientModel).filter(ClientModel.email == debug_data.email).first()
    if not client:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    results = {
        "email": client.email,
        "client_id": client.id_key,
        "stored_salt": client.password_salt[:10] + "...",
        "stored_hash": client.password_hash[:10] + "...",
        "tests": {}
    }

    old_hash = hashlib.sha256((debug_data.password + client.password_salt).encode()).hexdigest()
    results["tests"]["old_method"] = {
        "calculated": old_hash[:20] + "...",
        "stored": client.password_hash[:20] + "...",
        "matches": old_hash == client.password_hash
    }

    try:
        salt_bytes = base64.b64decode(client.password_salt)
        pbkdf2_hash = hashlib.pbkdf2_hmac(
            'sha256',
            debug_data.password.encode('utf-8'),
            salt_bytes,
            100000,
            dklen=32
        ).hex()
        results["tests"]["pbkdf2_method"] = {
            "calculated": pbkdf2_hash[:20] + "...",
            "stored": client.password_hash[:20] + "...",
            "matches": pbkdf2_hash == client.password_hash,
            "iterations": 100000
        }
    except Exception as e:
        results["tests"]["pbkdf2_method"] = {"error": str(e)}

    try:
        is_valid = AuthService.verify_password(debug_data.password, client.password_salt, client.password_hash)
        results["tests"]["auth_service"] = {"is_valid": is_valid}
    except Exception as e:
        results["tests"]["auth_service"] = {"error": str(e)}

    return results