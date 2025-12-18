import sys
sys.path.append('.')
from sqlalchemy.orm import Session
from config.database_render import SessionLocal

db = SessionLocal()

try:
    from repositories.client_repository import ClientRepository
    repo = ClientRepository(db)
    print("✅ ClientRepository OK")
except Exception as e:
    print(f"❌ ClientRepository Error: {e}")

try:
    from repositories.order_repository import OrderRepository
    repo = OrderRepository(db)
    print("✅ OrderRepository OK")
except Exception as e:
    print(f"❌ OrderRepository Error: {e}")

try:
    from repositories.product_repository import ProductRepository
    repo = ProductRepository(db)
    print("✅ ProductRepository OK")
except Exception as e:
    print(f"❌ ProductRepository Error: {e}")

db.close()