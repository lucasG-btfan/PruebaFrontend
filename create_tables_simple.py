# create_tables_simple.py
"""
Crear tablas directamente sin usar alembic.
"""
import os
import sys
from sqlalchemy import create_engine

# Agregar directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# URL de Render
DATABASE_URL = "postgresql://ecommerce_user:XuchJ7YFaWcfTnq4s1RX4CpTTGrxwfbG@dpg-d4mvsm1r0fns73ai8s10-a.ohio-postgres.render.com/ecommerce_db_sbeb"

print("🗂️ Creando tablas en Render...")

try:
    # Importar Base y modelos
    from models.base_model import Base
    from models.client import ClientModel
    from models.bill import BillModel
    from models.order import OrderModel
    from models.order_detail import OrderDetailModel
    from models.product import ProductModel
    from models.category import CategoryModel
    from models.address import AddressModel
    from models.review import ReviewModel
    
    print("✅ Modelos importados correctamente")
    
    # Crear engine
    engine = create_engine(DATABASE_URL)
    
    # Crear todas las tablas
    print("Creando tablas...")
    Base.metadata.create_all(engine)
    
    print("🎉 ¡TABLAS CREADAS EXITOSAMENTE!")
    print("\nTablas creadas:")
    for table in Base.metadata.tables:
        print(f"  • {table}")
        
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("\nAsegúrate de que todos los modelos tengan la clase correcta:")
    print("  - models/client.py debe tener: class Client(BaseModel)")
    print("  - models/__init__.py debe importar: from .client import Client")
    
except Exception as e:
    print(f"❌ Error creando tablas: {e}")
    import traceback
    traceback.print_exc()