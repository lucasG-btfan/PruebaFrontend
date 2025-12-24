from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from models.enums import DeliveryMethod, Status
import logging
import random

logger = logging.getLogger(__name__)

from models.order import OrderModel
from models.order_detail import OrderDetailModel
from models.client import ClientModel
from models.bill import BillModel
from models.enums import PaymentType

class OrderService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_simple_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea una orden simple
        """
        try:
            logger.info(f"Creando orden: {order_data}")
            
            client_id = order_data.get('client_id')
            client = self.db.query(ClientModel).filter(ClientModel.id_key == client_id).first()
            if not client:
                return {"success": False, "error": f"Cliente {client_id} no encontrado"}
            
            order_dict = {
                "client_id_key": client_id,
                "total": float(order_data.get('total', 0.0)),
                "delivery_method": DeliveryMethod.DRIVE_THRU,
                "status": Status.PENDING,
                "address": order_data.get('notes', ''),
                "date": datetime.utcnow()
            }
            
            
            order = OrderModel(**order_dict)
            self.db.add(order)
            self.db.commit()
            self.db.refresh(order)
            
            logger.info(f"Orden creada ID: {order.id_key}")
            
            order_details = order_data.get('order_details', [])
            for detail in order_details:
                detail_dict = {
                    "order_id": order.id_key,
                    "product_id": detail.get('product_id'),
                    "quantity": detail.get('quantity', 1),
                    "price": float(detail.get('price', 0.0))
                }
                detail_obj = OrderDetailModel(**detail_dict)
                self.db.add(detail_obj)
            
            self.db.commit()
            
            try:
                bill_number = f"FACT-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
                total_amount = float(order_data.get('total', 0.0))
                subtotal = total_amount / 1.21  #  21% IVA
                
                bill_dict = {
                    "bill_number": bill_number,
                    "order_id_key": order.id_key,  
                    "client_id_key": client_id,  
                    "total": total_amount,
                    "subtotal": subtotal,
                    "payment_type": PaymentType.CASH,
                    "discount": 0.0,
                    "date": datetime.now().date()
                }
                
                print(f"DEBUG: bill_dict antes de crear BillModel = {bill_dict}")
                print(f"DEBUG: client_id value = {client_id}")

                bill = BillModel(**bill_dict)
                self.db.add(bill)
                self.db.commit()
                self.db.refresh(bill)

                order.bill_id = bill.id_key  
                self.db.commit()
                
                return {
                    "success": True,
                    "message": "Orden y factura creadas exitosamente",
                    "order_id": order.id_key,
                    "bill_id": bill.id_key
                }
                
            except Exception as bill_error:
                logger.warning(f"Error creando factura: {bill_error}. Orden creada sin factura.")
                return {
                    "success": True,
                    "message": "Orden creada (factura pendiente)",
                    "order_id": order.id_key,
                    "bill_id": None
                }
                
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creando orden: {e}", exc_info=True)
            return {"success": False, "error": f"Error interno: {str(e)}"}
    
    def get_active_orders(self):
        """Obtener órdenes activas (estados PENDING e IN_PROGRESS)."""
        try:
            active_orders = self.db.query(OrderModel).filter(
                OrderModel.status.in_([Status.PENDING, Status.IN_PROGRESS])
            ).all()

            # Convierte las órdenes a un formato serializable 
            orders_list = []
            for order in active_orders:
                order_dict = {
                    "id_key": order.id_key,
                    "client_id": order.client_id_key,
                    "total": float(order.total) if order.total else 0.0,
                    "status": str(order.status),  
                    "delivery_method": str(order.delivery_method),  
                    "address": order.address,
                    "date": order.date.isoformat() if order.date else None,
                    "order_details": []
                }
                # Agrega los detalles de la orden si existen
                if hasattr(order, 'details') and order.details:
                    for detail in order.details:
                        order_dict["order_details"].append({
                            "product_id": detail.product_id,
                            "quantity": detail.quantity,
                            "price": float(detail.price) if detail.price else 0.0
                        })
                orders_list.append(order_dict)

            return orders_list

        except Exception as e:
            logger.error(f"Error obteniendo órdenes activas: {e}", exc_info=True)
            return []
    
    def get_order_by_id(self, order_id: int):
        """Obtener orden por ID"""
        try:
            order = self.db.query(OrderModel).filter(OrderModel.id_key == order_id).first()
            if order:
                
                self.db.refresh(order)
            return order
        except Exception as e:
            logger.error(f"Error obteniendo orden {order_id}: {e}")
            return None