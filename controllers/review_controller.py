from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from schemas.review_schema import ReviewCreate, ReviewUpdate, ReviewResponse
from services.review_service import ReviewService
from services.auth_service import AuthService
from repositories.review_repository import ReviewRepository
from repositories.order_repository import OrderRepository
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

def get_review_service(db: Session = Depends(get_db)):
    review_repo = ReviewRepository(db)
    order_repo = OrderRepository(db)
    return ReviewService(review_repo, order_repo)

def get_current_client_full(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Dependencia que obtiene el cliente completo desde BD"""
    return AuthService.get_current_client(credentials, db)

def get_current_client_simple(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Dependencia simple que solo verifica el token"""
    return AuthService.get_current_client_simple(credentials)

@router.post("/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review_data: ReviewCreate,
    current_client: dict = Depends(get_current_client_simple),  # ← Usar simple
    review_service: ReviewService = Depends(get_review_service),
    db: Session = Depends(get_db)  # Necesario para el servicio
):
    """Crear una nueva review para un producto comprado"""
    return review_service.create_review(review_data, current_client["id"])

@router.get("/reviews/product/{product_id}")
def get_product_reviews(
    product_id: int,
    review_service: ReviewService = Depends(get_review_service)
):
    """Obtener todas las reviews de un producto (público)"""
    reviews = review_service.get_product_reviews(product_id)
    return {
        "product_id": product_id,
        "reviews": reviews,
        "summary": review_service.get_product_rating_summary(product_id)
    }

@router.get("/reviews/order/{order_id}")
def get_order_reviews(
    order_id: int,
    current_client: dict = Depends(get_current_client_simple),
    db: Session = Depends(get_db)
):
    """Obtener reviews de una orden específica"""
    review_repo = ReviewRepository(db)
    reviews = review_repo.get_by_order(order_id)
    
    # Filtrar solo las reviews del cliente si no es admin
    if current_client["id"] != 0:
        reviews = [r for r in reviews if r.client_id == current_client["id"]]
    
    return reviews

@router.get("/reviews/me")
def get_my_reviews(
    current_client: dict = Depends(get_current_client_simple),
    review_service: ReviewService = Depends(get_review_service)
):
    """Obtener todas las reviews del cliente actual"""
    return review_service.get_client_reviews(current_client["id"])

@router.get("/reviews/{review_id}", response_model=ReviewResponse)
def get_review(
    review_id: int,
    current_client: dict = Depends(get_current_client_simple),
    review_service: ReviewService = Depends(get_review_service)
):
    """Obtener una review específica"""
    return review_service.get_review(review_id, current_client["id"])

@router.put("/reviews/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    update_data: ReviewUpdate,
    current_client: dict = Depends(get_current_client_simple),
    review_service: ReviewService = Depends(get_review_service)
):
    """Actualizar una review existente"""
    return review_service.update_review(review_id, update_data, current_client["id"])

@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    current_client: dict = Depends(get_current_client_simple),
    review_service: ReviewService = Depends(get_review_service)
):
    """Eliminar una review"""
    review_service.delete_review(review_id, current_client["id"])
    return None

@router.get("/products/{product_id}/rating")
def get_product_rating(
    product_id: int,
    review_service: ReviewService = Depends(get_review_service)
):
    """Obtener el rating promedio y resumen de un producto (público)"""
    return review_service.get_product_rating_summary(product_id)