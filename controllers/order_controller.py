from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from schemas.order_schema import OrderCreateSchema, OrderResponseSchema, OrderListSchema
from schemas.order_detail_schema import OrderDetailCreateSchema  
from models.order import OrderModel
from models.order_detail import OrderDetailModel
from models.product import ProductModel
from models.client import ClientModel
from models.bill import BillModel
from models.enums import Status
from services.order_detail_service import OrderDetailService  
from middleware.auth_middleware import get_current_user
import logging
from datetime import datetime
import uuid
from models.enums import PaymentType

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

        # Verificar que el usuario esté creando su propia orden
        if order_data.client_id_key != current_user.id_key:
            logger.warning(f"Intento de crear orden para otro usuario. Auth: {current_user.id_key}, Request: {order_data.client_id_key}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes crear órdenes para otros usuarios"
            )

        # Verificar que el cliente exista y esté activo
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

        # 1. Verificar que haya productos en la orden
        if not order_data.order_details or len(order_data.order_details) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La orden debe contener al menos un producto"
            )

        # 2. Verificar productos y calcular total
        total_calculated: float = 0
        order_items = []
        
        for detail in order_data.order_details:
            product: ProductModel | None = db.query(ProductModel).filter(
                ProductModel.id_key == detail.product_id
            ).first()

            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Producto no encontrado: {detail.product_id}"
                )

            # Verificar stock si el campo existe
            if hasattr(product, 'stock') and product.stock is not None:
                if product.stock < detail.quantity:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Stock insuficiente para {product.name}. Disponible: {product.stock}, Solicitado: {detail.quantity}"
                    )

            price: float = detail.price if detail.price is not None else product.price
            
            order_items.append({
                'product_id': detail.product_id,
                'quantity': detail.quantity,
                'price': price,
                'product': product
            })
            
            total_calculated += price * detail.quantity

        # 3. Verificar que el total coincida 
        if abs(total_calculated - order_data.total) > 1.00:  
            logger.warning(f"Total calculado ({total_calculated}) no coincide con enviado ({order_data.total})")
            order_data.total = round(total_calculated, 2)

        # 4. Crear la orden 
        order_dict = order_data.model_dump(exclude={'order_details', 'bill_id'})
        
        order = OrderModel(
            **order_dict,
            date=datetime.now()
        )

        db.add(order)
        db.flush()  

        # 5. Crear los detalles de la orden usando el servicio
        order_detail_service = OrderDetailService(db)
        
        for item in order_items:
            # Preparar datos para OrderDetail
            detail_schema = OrderDetailCreateSchema(
                order_id=order.id_key,
                product_id=item['product_id'],
                quantity=item['quantity'],
                price=item['price']
            )
            
            # Usar el servicio que maneja stock automáticamente
            order_detail = order_detail_service.save(detail_schema)
            logger.info(f"Detalle de orden creado: {order_detail.id_key}")

        bill_number = f"FACT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
        subtotal = round(order.total / 1.21, 2) if order.total > 0 else 0
        
        bill = BillModel(
            bill_number=bill_number,
            date=datetime.now(),
            total=order.total,
            subtotal=subtotal,
            payment_type=PaymentType.CASH,  
            discount=0.0,
            client_id_key=order.client_id_key,
            order_id_key=order.id_key
        )

        db.add(bill)
        db.flush()

        # 6. Actualizar la orden con el bill_id
        order.bill_id = bill.id_key

        db.commit()
        db.refresh(order)

        logger.info(f"Orden creada exitosamente: ID {order.id_key}, Factura: {bill_number}")

        return OrderResponseSchema(
            id_key=order.id_key,
            client_id_key=order.client_id_key,
            total=order.total,
            delivery_method=order.delivery_method,
            status=order.status,
            address=order.address,
            date=order.date,
            created_at=order.created_at if order.created_at else order.date,
            bill_id=order.bill_id,
            message="Orden creada exitosamente"
        )

    except HTTPException:
        db.rollback()
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
        # el cliente solo puede ver su propia orden
        if current_user.id_key != client_id and current_user.id_key != 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver estas órdenes"
            )

        orders: list[OrderModel] = db.query(OrderModel).filter(
            OrderModel.client_id_key == client_id
        ).order_by(OrderModel.date.desc()).all()

        return [
            OrderListSchema(
                id_key=order.id_key,
                client_id_key=order.client_id_key,
                total=order.total,
                status=order.status,
                date=order.date,
                address=order.address,
                bill_id=order.bill_id
            )
            for order in orders
        ]

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
        # Solo administradores pueden ver todas las órdenes
        if current_user.id_key != 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo administradores pueden ver todas las órdenes"
            )

        orders: list[OrderModel] = db.query(OrderModel).order_by(OrderModel.date.desc()).all()
        
        return [
            OrderListSchema(
                id_key=order.id_key,
                client_id_key=order.client_id_key,
                total=order.total,
                status=order.status,
                date=order.date,
                address=order.address,
                bill_id=order.bill_id
            )
            for order in orders
        ]

    except Exception as e:
        logger.error(f"Error obteniendo todas las órdenes: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/orders/{order_id}/details")
async def get_order_details(
    order_id: int,
    current_user: ClientModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener los detalles (productos) de una orden específica"""
    try:
        # Obtener la orden
        order: OrderModel | None = db.query(OrderModel).filter(
            OrderModel.id_key == order_id
        ).first()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orden no encontrada"
            )

        # Verificar permisos
        if current_user.id_key != order.client_id_key and current_user.id_key != 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver esta orden"
            )

        # Obtener detalles de la orden
        order_details = db.query(OrderDetailModel).filter(
            OrderDetailModel.order_id == order_id
        ).all()

        # Formatear respuesta
        details_response = []
        for detail in order_details:
            # Obtener información del producto
            product = db.query(ProductModel).filter(
                ProductModel.id_key == detail.product_id
            ).first()
            
            details_response.append({
                'id_key': detail.id_key,
                'product_id': detail.product_id,
                'product_name': product.name if product else 'Producto no encontrado',
                'quantity': detail.quantity,
                'price': detail.price,
                'subtotal': detail.quantity * detail.price,
                'created_at': detail.created_at
            })

        return {
            'order_id': order.id_key,
            'order_date': order.date,
            'order_total': order.total,
            'order_status': order.status.value,
            'order_details': details_response
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo detalles de la orden {order_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
    
@router.put("/orders/{order_id}/deliver")
async def mark_order_as_delivered(
    order_id: int,
    current_user: ClientModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marcar una orden como entregada (solo para admin)"""
    try:
        # Solo el admin puede marcar órdenes como entregadas
        if current_user.id_key != 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo administradores pueden marcar órdenes como entregadas"
            )

        order: OrderModel | None = db.query(OrderModel).filter(
            OrderModel.id_key == order_id
        ).first()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orden no encontrada"
            )

        if order.status == Status.DELIVERED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La orden ya está marcada como entregada"
            )

        # Verificar que no esté cancelada
        if order.status == Status.CANCELED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede marcar como entregada una orden cancelada"
            )

        order.status = Status.DELIVERED
        order.delivered_date = datetime.now()
        order.updated_at = datetime.now()

        db.commit()
        db.refresh(order)

        logger.info(f"Orden {order_id} marcada como entregada")

        return {
            "success": True,
            "message": f"Orden {order_id} marcada como entregada",
            "order_id": order_id,
            "status": "DELIVERED",
            "delivered_date": order.delivered_date.isoformat()
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error marcando orden {order_id} como entregada: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/orders/{order_id}/status")
async def get_order_status(
    order_id: int,
    current_user: ClientModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener el estado de una orden"""
    try:
        order: OrderModel | None = db.query(OrderModel).filter(
            OrderModel.id_key == order_id
        ).first()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orden no encontrada"
            )

        # Verificar permisos
        if current_user.id_key != order.client_id_key and current_user.id_key != 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver esta orden"
            )

        return {
            "order_id": order.id_key,
            "status": order.status.value,
            "status_code": order.status.value if isinstance(order.status, int) else 0,
            "status_display": order.status.name if hasattr(order.status, 'name') else str(order.status),
            "delivered_date": order.delivered_date.isoformat() if order.delivered_date else None,
            "can_review": order.status == Status.DELIVERED
        }

    except Exception as e:
        logger.error(f"Error obteniendo estado de la orden {order_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )