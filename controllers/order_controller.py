"""Order controller with proper dependency injection."""
from controllers.base_controller_impl import BaseControllerImpl
from schemas.order_schema import OrderSchema
from services.order_service import OrderService
from models.bill import Bill
from flask import request, current_app
from config.database_render import SessionLocal  # Importar SessionLocal

class OrderController(BaseControllerImpl):
    """Controller for Order entity with CRUD operations."""

    def __init__(self):
        super().__init__(
            schema=OrderSchema,
            service_factory=lambda db: OrderService(db),
            tags=["Orders"]
        )

    def create(self):
        """Override create method to handle automatic bill creation."""
        data = request.get_json()

        # Obtener sesión de base de datos
        db = SessionLocal()

        try:
            # Crear bill automáticamente si no existe
            if 'bill_id' not in data or not data.get('bill_id'):
                # Crear un bill con valores por defecto
                bill_data = {
                    'client_id': data.get('client_id'),
                    'total_amount': 0,  # Se puede actualizar después si es necesario
                    'payment_method': 'pending',
                    'status': 'pending'
                }
                bill = Bill(**bill_data)
                db.add(bill)
                db.commit()
                data['bill_id'] = bill.id
                current_app.logger.info(f"Bill created with ID: {bill.id}")

            # Continuar con la creación de la orden usando el método del padre
            return super().create()

        except Exception as e:
            db.rollback()
            current_app.logger.error(f"Error creating order: {e}")
            return {"error": str(e)}, 500

        finally:
            db.close()
