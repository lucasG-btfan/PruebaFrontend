from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from schemas.review_schema import ReviewCreate, ReviewUpdate, ReviewResponse
from services.review_service import ReviewService
from services.auth_service import AuthService
from repositories.review_repository import ReviewRepository
from repositories.order_repository import OrderRepository
from repositories.product_repository import ProductRepository  # Nuevo
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

def get_review_service(db: Session = Depends(get_db)):
    review_repo = ReviewRepository(db)
    order_repo = OrderRepository(db)
    product_repo = ProductRepository(db)
    return ReviewService(review_repo, order_repo, product_repo, db)  

def get_current_client_simple(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Dependencia simple que solo verifica el token."""
    return AuthService.get_current_client_simple(credentials)

@router.get("/reviews", response_model=List[ReviewResponse])
def get_all_reviews(
    skip: int = 0,
    limit: int = 100,
    review_service: ReviewService = Depends(get_review_service)
):
    """Obtener todas las reviews (público)."""
    try:
        logger.info(f"📋 Obteniendo todas las reseñas (skip={skip}, limit={limit})")
        return review_service.get_all_reviews(skip, limit)
    except Exception as e:
        logger.error(f"❌ Error obteniendo todas las reseñas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review_data: ReviewCreate,
    current_client: dict = Depends(get_current_client_simple),
    review_service: ReviewService = Depends(get_review_service)
):
    """Crear una nueva reseña (solo para cliente autenticado)."""
    logger.info(f"📝 Creando reseña - Cliente: {current_client['id']}")
    logger.info(f"📦 Datos: {review_data}")

    # Solo clientes normales pueden crear reviews 
    if current_client["id"] == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Los administradores no pueden crear reseñas"
        )

    try:
        result = review_service.create_review(review_data, current_client["id"])
        logger.info(f"✅ Reseña creada exitosamente: ID {result.id_key}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error al crear la reseña: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la reseña: {str(e)}"
        )

@router.get("/reviews/product/{product_id}", response_model=List[ReviewResponse])
def get_reviews_by_product(
    product_id: int,
    review_service: ReviewService = Depends(get_review_service)
):
    """Obtener todas las reseñas de un producto (público)."""
    try:
        logger.info(f"📋 Obteniendo reseñas del producto {product_id}")
        return review_service.get_product_reviews(product_id)
    except Exception as e:
        logger.error(f"❌ Error obteniendo reseñas del producto {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/reviews/product/{product_id}/rating")
def get_product_rating(
    product_id: int,
    review_service: ReviewService = Depends(get_review_service)
):
    """Obtener el promedio de calificación y resumen de un producto (público)."""
    try:
        logger.info(f"📊 Obteniendo resumen de calificaciones del producto {product_id}")
        return review_service.get_product_rating_summary(product_id)
    except Exception as e:
        logger.error(f"❌ Error obteniendo resumen de calificaciones del producto {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/reviews/me", response_model=List[ReviewResponse])
def get_my_reviews(
    current_client: dict = Depends(get_current_client_simple),
    review_service: ReviewService = Depends(get_review_service)
):
    """Obtener las reseñas del usuario actual (privado)."""
    try:
        logger.info(f"📋 Obteniendo reseñas del cliente {current_client['id']}")
        return review_service.get_client_reviews(current_client["id"])
    except Exception as e:
        logger.error(f"❌ Error obteniendo reseñas del cliente {current_client['id']}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/reviews/order/{order_id}", response_model=List[ReviewResponse])
def get_order_reviews(
    order_id: int,
    current_client: dict = Depends(get_current_client_simple),
    review_service: ReviewService = Depends(get_review_service)
):
    """Obtener reseñas de una orden específica (privado)."""
    try:
        logger.info(f"📋 Obteniendo reseñas de la orden {order_id} para el cliente {current_client['id']}")

        # Para admin, mostrar todas las reviews de la orden
        if current_client["id"] == 0:
            reviews = review_service.get_order_reviews(order_id)
        else:
            # Para cliente normal, solo sus propias reviews de esa orden
            reviews = review_service.get_reviews_by_order_and_client(
                order_id=order_id,
                client_id=current_client["id"]
            )

        return reviews
    except Exception as e:
        logger.error(f"❌ Error obteniendo reseñas de la orden {order_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/reviews/{review_id}", response_model=ReviewResponse)
def get_review(
    review_id: int,
    review_service: ReviewService = Depends(get_review_service)
):
    """Obtener una reseña específica por ID (público)."""
    try:
        logger.info(f"📋 Obteniendo reseña {review_id}")
        return review_service.get_review(review_id)
    except Exception as e:
        logger.error(f"❌ Error obteniendo reseña {review_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.put("/reviews/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    update_data: ReviewUpdate,
    current_client: dict = Depends(get_current_client_simple),
    review_service: ReviewService = Depends(get_review_service)
):
    """Actualizar una reseña existente (solo el cliente que la creó)."""
    try:
        logger.info(f"📝 Actualizando reseña {review_id} - Cliente: {current_client['id']}")
        updated_review = review_service.update_review(
            review_id=review_id,
            update_data=update_data,
            client_id=current_client["id"]
        )
        logger.info(f"✅ Reseña {review_id} actualizada exitosamente")
        return updated_review
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error actualizando reseña {review_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la reseña: {str(e)}"
        )

@router.delete("/reviews/{review_id}")
def delete_review(
    review_id: int,
    current_client: dict = Depends(get_current_client_simple),
    review_service: ReviewService = Depends(get_review_service)
):
    """Eliminar una reseña (solo el cliente que la creó o admin)."""
    try:
        logger.info(f"🗑️ Eliminando reseña {review_id} - Cliente: {current_client['id']}")
        success = review_service.delete_review(
            review_id=review_id,
            client_id=current_client["id"]
        )

        if success:
            logger.info(f"✅ Reseña {review_id} eliminada exitosamente")
            return {"message": f"Reseña {review_id} eliminada exitosamente"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo eliminar la reseña"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error eliminando reseña {review_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar la reseña: {str(e)}"
        )
