from sqlalchemy import Column, String, Float, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from models.base_model import BaseModel

class ReviewModel(BaseModel):
    __tablename__ = 'reviews'

    __table_args__ = (
        CheckConstraint('rating >= 1.0 AND rating <= 5.0', name='check_rating_range'),
    )

    id_key = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    rating = Column(Float, nullable=False)
    comment = Column(String)
    product_id = Column(Integer, ForeignKey('products.id_key'), index=True)

    # Relación
    product = relationship('ProductModel', back_populates='reviews', lazy='select')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Review(id_key={self.id_key}, rating={self.rating})>"
