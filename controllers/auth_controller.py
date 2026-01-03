from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from schemas.client_schema import ClientLoginSchema, ClientRegisterSchema, ClientModel
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
async def login(login_data: ClientLoginSchema, db: Session = Depends(get_db)):
    """Login endpoint."""
    client = db.query(ClientModel).filter(
        ClientModel.email == login_data.email,
        ClientModel.is_active == True
    ).first()
    
    if not client:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not AuthService.verify_password(
        login_data.password.get_secret_value(),
        client.password_salt,
        client.password_hash
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "message": "Login successful",
        "client_id": client.id_key,
        "email": client.email,
        "name": f"{client.name} {client.lastname}"
    }

@router.post("/register")
async def register(register_data: ClientRegisterSchema, db: Session = Depends(get_db)):
    """Register endpoint."""
    # Check if email exists
    existing = db.query(ClientModel).filter(
        ClientModel.email == register_data.email
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check passwords match
    if register_data.password.get_secret_value() != register_data.confirm_password.get_secret_value():
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    # Generate salt and hash password
    salt = AuthService.generate_salt()
    password_hash = AuthService.hash_password(
        register_data.password.get_secret_value(),
        salt
    )
    
    # Create client
    client_data = register_data.dict(exclude={'password', 'confirm_password'})
    client = ClientModel(
        **client_data,
        password_hash=password_hash,
        password_salt=salt
    )
    
    db.add(client)
    db.commit()
    db.refresh(client)
    
    return {
        "message": "Registration successful",
        "client_id": client.id_key,
        "email": client.email
    }