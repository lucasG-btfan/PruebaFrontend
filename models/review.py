from __future__ import annotations

from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base

class ReviewModel(Base):
    __tablename__ = "reviews"

    id_key = Column(Integer, primary_key=True, index=True)
    rating = Column(Float, nullable=False)
    comment = Column(Text, nullable=True)
    product_id = Column(Integer, ForeignKey("products.id_key"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id_key"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id_key"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Constraints
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )

    # Relaciones
    product = relationship("ProductModel", back_populates="reviews")
    client = relationship("ClientModel", back_populates="reviews")
    order = relationship("OrderModel")
