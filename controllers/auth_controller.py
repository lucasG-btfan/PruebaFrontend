from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from config.database import get_db
from schemas.client_schema import ClientLoginSchema, ClientRegisterSchema
from models.client import ClientModel
from services.auth_service import AuthService
from jose import jwt
from middleware.auth_middleware import get_current_user  
import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Authentication"])

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user_id_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        client_id_str = payload.get("sub")

        if client_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        return int(client_id_str)

    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

@router.post("/login")
async def login(login_data: ClientLoginSchema, db: Session = Depends(get_db)):
    """Login endpoint - Permitir admin con id_key=0."""
    logger.info(f"Login attempt for email: {login_data.email}")

    client = db.query(ClientModel).filter(
        ClientModel.email == login_data.email,
        ClientModel.is_active == True
    ).first()

    if not client:
        logger.warning(f"Client not found or inactive: {login_data.email}")
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if not AuthService.verify_password(
        login_data.password.get_secret_value(),
        client.password_salt,
        client.password_hash
    ):
        logger.warning(f"Invalid password for: {login_data.email}")
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    access_token = create_access_token(data={"sub": str(client.id_key)})

    logger.info(f"Login successful for: {login_data.email}")
    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "client_id": client.id_key,
        "email": client.email,
        "name": f"{client.name} {client.lastname}"
    }

@router.post("/register")
async def register(register_data: ClientRegisterSchema, db: Session = Depends(get_db)):
    """Register endpoint - Solo para clientes normales (no admin)."""
    logger.info(f"Registration attempt for email: {register_data.email}")

    existing = db.query(ClientModel).filter(
        ClientModel.email == register_data.email
    ).first()

    if existing:
        logger.warning(f"Email already registered: {register_data.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    if register_data.password.get_secret_value() != register_data.confirm_password.get_secret_value():
        logger.warning(f"Passwords don't match for: {register_data.email}")
        raise HTTPException(status_code=400, detail="Passwords do not match")

    if register_data.id_key == 0:
        raise HTTPException(status_code=403, detail="Forbidden: Cannot register admin user")

    salt = AuthService.generate_salt()
    password_hash = AuthService.hash_password(
        register_data.password.get_secret_value(),
        salt
    )

    client_data = register_data.dict(exclude={'password', 'confirm_password'})
    client = ClientModel(
        **client_data,
        password_hash=password_hash,
        password_salt=salt
    )

    db.add(client)
    db.commit()
    db.refresh(client)

    logger.info(f"Registration successful for: {register_data.email}, ID: {client.id_key}")
    return {
        "message": "Registration successful",
        "client_id": client.id_key,
        "email": client.email
    }

@router.get("/verify")
async def verify_token(
    current_user_id_key: int = Depends(get_current_user_id_key)
):
    """Verificar que el token es válido."""
    return {
        "valid": True,
        "client_id": current_user_id_key,
        "message": "Token válido"
    }

@router.get("/me")
async def get_me(current_user: ClientModel = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return {
        "id": current_user.id_key,
        "email": current_user.email,
        "name": f"{current_user.name} {current_user.lastname}",
        "is_admin": current_user.id_key == 0
    }
