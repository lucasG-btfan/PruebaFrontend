from __future__ import annotations
from sqlalchemy.orm import Session
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models.review import ReviewModel

class ReviewRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, review: ReviewModel) -> ReviewModel:
        self.session.add(review)
        self.session.commit()
        self.session.refresh(review)
        return review

    def get_by_id(self, review_id: int) -> Optional[ReviewModel]:
        from models.review import ReviewModel
        return self.session.query(ReviewModel).filter(ReviewModel.id_key == review_id).first()

    def get_by_product_and_client(self, product_id: int, client_id: int, order_id: int) -> Optional[ReviewModel]:
        from models.review import ReviewModel
        return self.session.query(ReviewModel).filter(
            ReviewModel.product_id == product_id,
            ReviewModel.client_id == client_id,
            ReviewModel.order_id == order_id
        ).first()

    def get_by_product(self, product_id: int) -> List[ReviewModel]:
        from models.review import ReviewModel
        return self.session.query(ReviewModel).filter(ReviewModel.product_id == product_id).all()

    def get_by_client(self, client_id: int) -> List[ReviewModel]:
        from models.review import ReviewModel
        return self.session.query(ReviewModel).filter(ReviewModel.client_id == client_id).all()

    def get_by_client_product_order(self, client_id: int, product_id: int, order_id: int):
        from models.review import ReviewModel
        return self.session.query(ReviewModel).filter(
            ReviewModel.client_id == client_id,
            ReviewModel.product_id == product_id,
            ReviewModel.order_id == order_id
        ).first()

    def get_by_order(self, order_id: int) -> List[ReviewModel]:
        from models.review import ReviewModel
        return self.session.query(ReviewModel).filter(ReviewModel.order_id == order_id).all()

    def update(self, review_id: int, rating: Optional[float] = None, comment: Optional[str] = None) -> Optional[ReviewModel]:
        from models.review import ReviewModel
        review = self.get_by_id(review_id)
        if review:
            if rating is not None:
                review.rating = rating
            if comment is not None:
                review.comment = comment
            self.session.commit()
            self.session.refresh(review)
        return review

    def delete(self, review_id: int) -> bool:
        from models.review import ReviewModel
        review = self.get_by_id(review_id)
        if review:
            self.session.delete(review)
            self.session.commit()
            return True
        return False

    def get_product_average_rating(self, product_id: int) -> Optional[float]:
        from models.review import ReviewModel
        from sqlalchemy import func
        result = self.session.query(func.avg(ReviewModel.rating)).filter(
            ReviewModel.product_id == product_id
        ).scalar()
        return float(result) if result else None

    def get_product_review_count(self, product_id: int) -> int:
        from models.review import ReviewModel
        return self.session.query(ReviewModel).filter(ReviewModel.product_id == product_id).count()
