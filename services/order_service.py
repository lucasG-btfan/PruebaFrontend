from datetime import datetime
from typing import Dict, Any, TYPE_CHECKING
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from schemas.order_schema import OrderSchema
    from schemas.order_detail_schema import OrderDetailSchema

from repositories.order_repository import OrderRepository
from repositories.order_detail_repository import OrderDetailRepository
from repositories.client_repository import ClientRepository
from services.bill_service import BillService

class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.order_detail_repo = OrderDetailRepository(db)
        self.client_repo = ClientRepository(db)
        self.bill_service = BillService(db)
    
    def create_simple_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea una orden simple con sus detalles
        """
        try:
            client_id = order_data.get('client_id')
            client = self.client_repo.get_by_id(client_id)
            if not client:
                return {"error": f"Cliente con ID {client_id} no encontrado", "success": False}
            
            order_dict = {
                "client_id_key": client_id,  
                "total": order_data.get('total', 0.0),
                "delivery_method": order_data.get('delivery_method', 1),
                "status": order_data.get('status', 1),  
                "notes": order_data.get('notes', ''),
                "date": datetime.utcnow()
            }
            
            order = self.order_repo.create(order_dict)
            
            order_details = order_data.get('order_details', [])
            for detail in order_details:
                detail_dict = {
                    "order_id": order.id_key,  
                    "product_id": detail.get('product_id'),
                    "quantity": detail.get('quantity', 1),
                    "price": detail.get('price', 0.0)
                }
                self.order_detail_repo.create(detail_dict)
            
            try:
                bill_data = {
                    "order_id": order.id_key,
                    "client_id": client_id,
                    "subtotal": order.total,
                    "taxes": order.total * 0.21, 
                    "total": order.total * 1.21,
                    "payment_method": 1  
                }
                bill = self.bill_service.create_bill(bill_data)
                
                self.order_repo.update(order.id_key, {"bill_id": bill.id_key})
                
                return {
                    "success": True,
                    "message": "Orden y factura creadas exitosamente",
                    "order_id": order.id_key,
                    "bill_id": bill.id_key
                }
            except Exception as bill_error:
                return {
                    "success": True,
                    "message": f"Orden creada pero factura falló: {str(bill_error)}",
                    "order_id": order.id_key,
                    "bill_id": None
                }
                
        except Exception as e:
            return {"error": f"Error al crear orden: {str(e)}", "success": False}
    
    def get_all_orders(self):
        """Obtiene todas las órdenes con sus relaciones"""
        return self.order_repo.get_all()
    
    def get_order_by_id(self, order_id: int):
        """Obtiene una orden por ID con detalles"""
        order = self.order_repo.get_by_id(order_id)
        if order:
            self.db.refresh(order)
        return order