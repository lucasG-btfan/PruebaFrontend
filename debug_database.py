# debug_database.py
import sys
import os

# Agregar directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

print("🔍 Starting database debug...")

try:
    # Probar importación de config
    from config import engine, DATABASE_URL, check_connection
    print(f"✅ Config imported. DATABASE_URL: {DATABASE_URL[:60]}...")
    
    # Probar conexión
    print("🔗 Testing connection...")
    success = check_connection()
    print(f"✅ Connection test: {'SUCCESS' if success else 'FAILED'}")
    
    # Probar importación de modelos
    print("📦 Testing models import...")
    from models.base_model import Base
    print(f"✅ Base imported: {Base}")
    
    from models import ClientModel, ProductModel
    print(f"✅ Models imported: ClientModel={ClientModel}, ProductModel={ProductModel}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()