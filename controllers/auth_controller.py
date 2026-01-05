from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from schemas.client_schema import ClientLoginSchema, ClientRegisterSchema
from models.client import ClientModel
from services.auth_service import AuthService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])

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

    logger.info(f"Login successful for: {login_data.email}")
    return {
        "message": "Login successful",
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
