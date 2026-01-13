from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from schemas.order_schema import OrderCreateSchema, OrderResponseSchema, OrderListSchema
from models.order import OrderModel
from models.order_detail import OrderDetailModel
from models.product import ProductModel
from models.client import ClientModel
from middleware.auth_middleware import get_current_user
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Orders"])

@router.post("/orders", response_model=OrderResponseSchema)
async def create_order(
    order_data: OrderCreateSchema,
    current_user: ClientModel = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> OrderResponseSchema:
    try:
        logger.info(f"Creando orden para usuario ID: {current_user.id_key}")

        if order_data.client_id_key != current_user.id_key:
            logger.warning(f"Intento de crear orden para otro usuario. Auth: {current_user.id_key}, Request: {order_data.client_id_key}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes crear órdenes para otros usuarios"
            )

        client: ClientModel | None = db.query(ClientModel).filter(
            ClientModel.id_key == order_data.client_id_key,
            ClientModel.is_active == True
        ).first()

        if not client:
            logger.warning(f"Cliente no encontrado o inactivo: {order_data.client_id_key}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado o inactivo"
            )

        order_number: str = f"ORD-{uuid.uuid4().hex[:8].upper()}-{datetime.now().strftime('%Y%m%d')}"
        order_dict: dict = order_data.model_dump(exclude={'order_details'})

        order: OrderModel = OrderModel(
            **order_dict,
            order_number=order_number,
            date=datetime.now()
        )

        db.add(order)
        db.flush()

        total_calculated: float = 0
        for detail in order_data.order_details:
            product: ProductModel | None = db.query(ProductModel).filter(
                ProductModel.id_key == detail.product_id
            ).first()

            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Producto no encontrado: {detail.product_id}"
                )

            price: float = detail.price if detail.price is not None else product.price

            order_detail: OrderDetailModel = OrderDetailModel(
                order_id=order.id_key,
                product_id=detail.product_id,
                quantity=detail.quantity,
                price=price
            )

            db.add(order_detail)
            total_calculated += price * detail.quantity

        if abs(total_calculated - order.total) > 0.01:
            order.total = total_calculated

        db.commit()
        db.refresh(order)

        logger.info(f"Orden creada exitosamente: {order_number} (ID: {order.id_key})")

        return OrderResponseSchema(
            id_key=order.id_key,
            order_number=order_number,
            client_id_key=order.client_id_key,
            total=order.total,
            delivery_method=order.delivery_method,
            status=order.status,
            address=order.address,
            date=order.date,
            created_at=order.date,
            message="Orden creada exitosamente"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando orden: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/orders/client/{client_id}", response_model=List[OrderListSchema])
async def get_client_orders(
    client_id: int,
    current_user: ClientModel = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[OrderListSchema]:
    try:
        if current_user.id_key != client_id and current_user.id_key != 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver estas órdenes"
            )

        orders: list[OrderModel] = db.query(OrderModel).filter(
            OrderModel.client_id_key == client_id
        ).order_by(OrderModel.date.desc()).all()

        return orders

    except Exception as e:
        logger.error(f"Error obteniendo órdenes del cliente {client_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/orders", response_model=List[OrderListSchema])
async def get_all_orders(
    current_user: ClientModel = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[OrderListSchema]:
    try:
        if current_user.id_key != 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo administradores pueden ver todas las órdenes"
            )

        orders: list[OrderModel] = db.query(OrderModel).order_by(OrderModel.date.desc()).all()
        return orders

    except Exception as e:
        logger.error(f"Error obteniendo todas las órdenes: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
