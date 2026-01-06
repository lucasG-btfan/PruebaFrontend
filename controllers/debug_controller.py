# controllers/debug_controller.py
from fastapi import APIRouter, Request, Header, Query
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/debug/headers")
async def debug_headers(request: Request):
    """Muestra TODOS los headers de la request"""
    headers = dict(request.headers)
    
    # Log detallado
    logger.info("🔍 Headers recibidos:")
    for key, value in headers.items():
        logger.info(f"  {key}: {value}")
    
    return {
        "method": request.method,
        "url": str(request.url),
        "headers": headers,
        "query_params": dict(request.query_params)
    }

@router.get("/debug/token")
async def debug_token(
    authorization: str = Header(None),
    token: str = Query(None)
):
    """Debug del token JWT"""
    logger.info(f"🔍 Authorization header: {authorization}")
    logger.info(f"🔍 Token query param: {token}")
    
    result = {
        "authorization_header": authorization,
        "token_query_param": token,
        "message": "Token debug endpoint"
    }
    
    if authorization:
        if authorization.startswith("Bearer "):
            token_from_header = authorization[7:]
            result["token_from_header"] = token_from_header[:50] + "..." if len(token_from_header) > 50 else token_from_header
            result["header_format"] = "Bearer token"
        else:
            result["header_format"] = "Raw token"
    
    return result