from repositories.review_repository import ReviewRepository
from repositories.order_repository import OrderRepository
from schemas.review_schema import ReviewCreate, ReviewUpdate
from models.review import ReviewModel
from typing import List, Optional
from fastapi import HTTPException, status
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models.review import ReviewModel

class ReviewService:
    def __init__(self, review_repo: ReviewRepository, order_repo: OrderRepository):
        self.review_repo = review_repo
        self.order_repo = order_repo
    
    def create_review(self, review_data: ReviewCreate, client_id: int):
        product = self.product_repo.get_by_id(review_data.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        order = self.order_repo.get_by_id(review_data.order_id)
        if not order or order.client_id != client_id:
            raise HTTPException(status_code=403, detail="No tienes permiso para reseñar esta orden")

        order_details = self.order_repo.get_order_details(review_data.order_id)
        if review_data.product_id not in [detail.product_id for detail in order_details]:
            raise HTTPException(status_code=400, detail="El producto no está en esta orden")

        # Crear la reseña
        review = ReviewModel(
            rating=review_data.rating,
            comment=review_data.comment,
            product_id=review_data.product_id,
            client_id=client_id,
            order_id=review_data.order_id
        )
        return self.review_repo.create(review)

    def get_review(self, review_id: int):
        review = self.review_repo.get_by_id(review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Reseña no encontrada")
        return review
    
    def get_product_reviews(self, product_id: int) -> List[ReviewModel]:
        return self.review_repo.get_by_product(product_id)
    
    def get_client_reviews(self, client_id: int) -> List[ReviewModel]:
        return self.review_repo.get_by_client(client_id)
    
    def update_review(self, review_id: int, update_data: ReviewUpdate, client_id: int) -> ReviewModel:
        review = self.review_repo.get_by_id(review_id)
        
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review no encontrada"
            )
        
        # Solo el cliente que creó la review puede actualizarla
        if review.client_id != client_id and client_id != 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para actualizar esta review"
            )
        
        return self.review_repo.update(
            review_id=review_id,
            rating=update_data.rating,
            comment=update_data.comment
        )
    
    def delete_review(self, review_id: int, client_id: int) -> bool:
        review = self.review_repo.get_by_id(review_id)
        
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review no encontrada"
            )
        
        # Solo el cliente que creó la review o admin puede eliminarla
        if review.client_id != client_id and client_id != 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para eliminar esta review"
            )
        
        return self.review_repo.delete(review_id)
    
    def get_product_rating_summary(self, product_id: int) -> dict:
        avg_rating = self.review_repo.get_product_average_rating(product_id)
        review_count = self.review_repo.get_product_review_count(product_id)
        
        return {
            "average_rating": avg_rating,
            "review_count": review_count,
            "rating_distribution": self._get_rating_distribution(product_id)
        }
    
    def _get_rating_distribution(self, product_id: int) -> dict:
        from sqlalchemy import func
        from models.review import ReviewModel
        distribution = self.review_repo.session.query(
            ReviewModel.rating,
            func.count(ReviewModel.id_key)
        ).filter(
            ReviewModel.product_id == product_id
        ).group_by(ReviewModel.rating).all()
        return {str(rating): count for rating, count in distribution}
