from models.bill import BillModel
from models.order import OrderModel
from models.client import ClientModel
from models.enums import DeliveryMethod, Status, PaymentType
from datetime import datetime

print("=== Verificando relaciones ===")

# 1. Verificar columnas de BillModel
print("\n1. Columnas de BillModel:")
for column in BillModel.__table__.columns:
    print(f"  - {column.name}")

# 2. Verificar columnas de OrderModel
print("\n2. Columnas de OrderModel:")
for column in OrderModel.__table__.columns:
    print(f"  - {column.name}")

# 3. Verificar relación Bill → Order (solo imprimir la configuración)
print("\n3. Relación Bill → Order:")
bill_rel = BillModel.order.property
print(f"  - Relación configurada: {bill_rel}")
print(f"  - Argumentos de la relación: {bill_rel.__dict__.get('_argument', {})}")

# 4. Verificar relación Order → Bill (solo imprimir la configuración)
print("\n4. Relación Order → Bill:")
order_rel = OrderModel.bill.property
print(f"  - Relación configurada: {order_rel}")
print(f"  - Argumentos de la relación: {order_rel.__dict__.get('_argument', {})}")

# 5. Prueba de creación
print("\n5. Prueba de creación:")

try:
    # Crear instancias de prueba
    order = OrderModel(
        total=100.0,
        delivery_method=DeliveryMethod.DRIVE_THRU,
        status=Status.PENDING,
        address="Test Address",
        client_id_key=1
    )
    print("  ✅ OrderModel creado")

    bill = BillModel(
        bill_number="TEST-001",
        order_id_key=1,  # Asegúrate de que este ID exista en la base de datos
        client_id_key=1,
        total=100.0,
        subtotal=82.64,
        payment_type=PaymentType.CASH.value,
        discount=0.0,
        date=datetime.now()
    )
    print("  ✅ BillModel creado")

    # Establecer relación bidireccional
    order.bill = bill
    bill.order = order

    print("  ✅ Relaciones establecidas")

except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()
