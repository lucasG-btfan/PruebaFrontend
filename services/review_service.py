from repositories.review_repository import ReviewRepository
from repositories.order_repository import OrderRepository
from repositories.product_repository import ProductRepository
from schemas.review_schema import ReviewCreate, ReviewUpdate
from models.review import ReviewModel
from models.product import ProductModel
from models.order import OrderModel
from models.order_detail import OrderDetailModel  
from models.enums import Status
from typing import List, Optional
from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy.orm import Session

class ReviewService:
    def __init__(self, 
                 review_repo: ReviewRepository, 
                 order_repo: OrderRepository,
                 product_repo: ProductRepository,
                 db: Session):  
        self.review_repo = review_repo
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.db = db
    
    def create_review(self, review_data: ReviewCreate, client_id: int):
        """Crear una nueva reseña con validaciones."""
        try:
            product = self.db.query(ProductModel).filter(
                ProductModel.id_key == review_data.product_id
            ).first()
            
            if not product:
                raise HTTPException(
                    status_code=404, 
                    detail="Producto no encontrado"
                )
            
            # 2. Verificar orden existe y pertenece al cliente
            order = self.db.query(OrderModel).filter(
                OrderModel.id_key == review_data.order_id
            ).first()
            
            if not order:
                raise HTTPException(
                    status_code=404, 
                    detail="Orden no encontrada"
                )
            
            if order.client_id_key != client_id:
                raise HTTPException(
                    status_code=403, 
                    detail="No tienes permiso para reseñar esta orden"
                )
            
            if order.status != Status.DELIVERED:
                raise HTTPException(
                    status_code=400,
                    detail="Solo puedes calificar productos de órdenes entregadas"
                )
            
            order_detail = self.db.query(OrderDetailModel).filter(
                OrderDetailModel.order_id == review_data.order_id,
                OrderDetailModel.product_id == review_data.product_id
            ).first()
            
            if not order_detail:
                raise HTTPException(
                    status_code=400, 
                    detail="El producto no está en esta orden"
                )
            
            existing_review = self.review_repo.get_by_client_product_order(
                client_id=client_id,
                product_id=review_data.product_id,
                order_id=review_data.order_id
            )
            
            if existing_review:
                raise HTTPException(
                    status_code=400,
                    detail="Ya has calificado este producto de esta orden"
                )
            
            review = ReviewModel(
                rating=review_data.rating,
                comment=review_data.comment,
                product_id=review_data.product_id,
                client_id=client_id,
                order_id=review_data.order_id,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            return self.review_repo.create(review)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al crear la reseña: {str(e)}"
            )
    
    def get_review(self, review_id: int):
        """Obtener una reseña específica (público)."""
        review = self.review_repo.get_by_id(review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Reseña no encontrada")
        return review
    
    def get_all_reviews(self, skip: int = 0, limit: int = 100) -> List[ReviewModel]:
        """Obtener todas las reseñas."""
        from models.review import ReviewModel
        return self.db.query(ReviewModel).offset(skip).limit(limit).all()
    
    def get_product_reviews(self, product_id: int) -> List[ReviewModel]:
        """Obtener todas las reseñas de un producto (público)."""
        return self.review_repo.get_by_product(product_id)
    
    def get_order_reviews(self, order_id: int) -> List[ReviewModel]:
        """Obtener todas las reseñas de una orden."""
        return self.review_repo.get_by_order(order_id)
    
    def get_client_reviews(self, client_id: int) -> List[ReviewModel]:
        """Obtener todas las reseñas de un cliente."""
        return self.review_repo.get_by_client(client_id)
    
    def update_review(self, review_id: int, update_data: ReviewUpdate, client_id: int) -> ReviewModel:
        """Actualizar una reseña (solo el cliente que la creó)."""
        review = self.review_repo.get_by_id(review_id)
        
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review no encontrada"
            )
        
        # Solo el cliente que creó la review puede actualizarla
        if review.client_id != client_id:
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
        """Eliminar una reseña (solo el cliente que la creó o admin)."""
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
        """Obtener resumen de calificaciones de un producto (público)."""
        avg_rating = self.review_repo.get_product_average_rating(product_id)
        review_count = self.review_repo.get_product_review_count(product_id)
        
        return {
            "average_rating": avg_rating or 0,
            "review_count": review_count or 0,
            "rating_distribution": self._get_rating_distribution(product_id)
        }
    
    def _get_rating_distribution(self, product_id: int) -> dict:
        """Obtener distribución de calificaciones (privado)."""
        distribution = {}
        reviews = self.review_repo.get_by_product(product_id)
        
        for i in range(1, 6):
            count = sum(1 for review in reviews if review.rating == i)
            distribution[str(i)] = count
        
        return distribution
    
    def get_reviews_by_order_and_client(self, order_id: int, client_id: int) -> List[ReviewModel]:
        """Obtener reseñas de una orden específica para un cliente."""
        from models.review import ReviewModel
        return self.db.query(ReviewModel).filter(
            ReviewModel.order_id == order_id,
            ReviewModel.client_id == client_id
        ).all()