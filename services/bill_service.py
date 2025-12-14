from sqlalchemy.orm import Session
from models.bill import BillModel
from repositories.bill_repository import BillRepository
from schemas.bill_schema import BillSchema, BillCreate
from services.base_service_impl import BaseServiceImpl
from datetime import datetime

class BillService(BaseServiceImpl):
    def __init__(self, db: Session):
        super().__init__(
            repository_class=BillRepository,
            model=BillModel,
            schema=BillSchema,
            db=db
        )

    def create_bill(self, bill_data: BillCreate) -> BillModel:
        """Crear una factura en la base de datos"""
        db_bill = BillModel(
            bill_number=bill_data.bill_number,
            date=datetime.now().date(),
            total=bill_data.total,
            discount=bill_data.discount,
            payment_type=bill_data.payment_type,
            client_id_key=bill_data.client_id_key,
            order_id_key=bill_data.order_id_key
        )
        self.db.add(db_bill)
        self.db.commit()
        self.db.refresh(db_bill)
        return db_bill

    def get_bill_by_id(self, bill_id: int) -> BillModel:
        """Obtener factura por ID"""
        return self.db.query(BillModel).filter(BillModel.id_key == bill_id).first()

    def get_bills(self, skip: int = 0, limit: int = 100) -> list[BillModel]:
        """Obtener lista de facturas"""
        return self.db.query(BillModel).offset(skip).limit(limit).all()

    def get_bill_by_order_id(self, order_id: int) -> BillModel:
        """Obtener factura por ID de orden"""
        return self.db.query(BillModel).filter(BillModel.order_id_key == order_id).first()
