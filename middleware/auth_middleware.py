from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt
from config.database import get_db
from models.client import ClientModel
import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        client_id = payload.get("sub")
        
        if client_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        client = db.query(ClientModel).filter(
            ClientModel.id_key == int(client_id),
            ClientModel.is_active == True
        ).first()
        
        if not client:
            raise HTTPException(status_code=401, detail="User not found")
        
        return client
        
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")