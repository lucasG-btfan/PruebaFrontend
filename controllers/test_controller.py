# controllers/test_controller.py
from fastapi import APIRouter
from typing import List

router = APIRouter()

@router.get("/test/clients")
async def test_clients():
    """Test endpoint returning mock data."""
    return {
        "items": [
            {"id_key": 1, "name": "John", "lastname": "Doe", "email": "john@example.com"},
            {"id_key": 2, "name": "Jane", "lastname": "Smith", "email": "jane@example.com"}
        ],
        "total": 2,
        "page": 1,
        "size": 10,
        "pages": 1
    }