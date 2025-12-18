from sqlalchemy.orm import Session
from models.bill import BillModel
from repositories.bill_repository import BillRepository
from schemas.bill_schema import BillCreate, BillResponse
from services.base_service_impl import BaseServiceImpl
from datetime import datetime, timedelta
import random

class BillService:
    def __init__(self, db: Session):
        self.db = db
        self.bill_repo = BillRepository(db)

    def generate_bill_number(self):
        """Generar un número de factura único."""
        return f"FACT-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

    def create_bill(self, bill_data: BillCreate) -> BillModel:
        """
        Crea una factura automáticamente para una orden.
        """
        bill_number = self.generate_bill_number()
        subtotal = bill_data.subtotal
        tax_rate = 0.21  
        tax_amount = subtotal * tax_rate 
        total = subtotal + tax_amount  


        bill_dict = {
            "bill_number": bill_number,
            "order_id_key": bill_data.order_id_key,
            "client_id_key": bill_data.client_id_key,
            "subtotal": subtotal,
            "taxes": tax_amount,
            "total": total,
            "payment_type": bill_data.payment_type,
            "status": 1,  
            "date": datetime.now().date(),
            "due_date": datetime.utcnow() + timedelta(days=30)
        }

        return self.bill_repo.create(bill_dict)

    def get_bill_by_order(self, order_id: int) -> BillModel:
        """Obtiene la factura asociada a una orden."""
        return self.bill_repo.get_by_order_id(order_id)

    def get_bill_by_id(self, bill_id: int) -> BillModel:
        """Obtener factura por ID."""
        return self.bill_repo.get_by_id(bill_id)

    def get_bills(self, skip: int = 0, limit: int = 100) -> list[BillModel]:
        """Obtener lista de facturas."""
        return self.bill_repo.get_all(skip=skip, limit=limit)

    def get_bills_by_client(self, client_id: int) -> list[BillModel]:
        """Obtener facturas por ID de cliente."""
        return self.bill_repo.get_by_client_id(client_id)
    
