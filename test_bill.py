# test_bill.py
from models.bill import BillModel

# Verificar los nombres de columnas
print("Columnas de BillModel:")
for column in BillModel.__table__.columns:
    print(f"  - {column.name} ({column.type})")

# Probar creación
test_data = {
    "bill_number": "TEST-123",
    "order_id": 1,
    "client_id_key": 1,
    "total": 100.0,
    "subtotal": 82.64,
    "payment_type": 1,
    "discount": 0.0,
    "date": "2023-12-21"
}

try:
    bill = BillModel(**test_data)
    print("✅ BillModel creado exitosamente con client_id_key")
except Exception as e:
    print(f"❌ Error: {e}")