# test_imports.py
import os
import sys
import traceback

# Agregar directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🧪 Probando importaciones y configuración...")

# Test 1: SQLAlchemy básico
try:
    from sqlalchemy import Integer, String, DateTime, Float, Boolean
    print("✅ SQLAlchemy tipos importados correctamente")
except ImportError as e:
    print(f"❌ Error al importar tipos de SQLAlchemy: {e}")

# Test 2: Base y BaseModel (ejecutar fix si es necesario)
try:
    from models.base_model import Base, BaseModel
    print("✅ Base y BaseModel importados correctamente")
except ImportError as e:
    print(f"⚠️ BaseModel no encontrado. Intentando corregir...")
    try:
        exec(open('fix_base_model.py').read())
        from models.base_model import Base, BaseModel
        print("✅ Base y BaseModel importados después de corregir")
    except Exception as e:
        print(f"❌ Error al corregir BaseModel: {e}")
        traceback.print_exc()

# Test 3: Modelos específicos
try:
    from models.client import ClientModel
    from models.bill import Bill
    print("✅ Modelos Client y Bill importados correctamente")
except ImportError as e:
    print(f"⚠️ Algunos modelos no se pudieron importar: {e}")

# Test 4: Schemas (opcional)
try:
    from schemas import *
    print("✅ Schemas importados correctamente")
except ImportError as e:
    print(f"⚠️ Schemas no disponibles: {e}")

# Test 5: Database y conexión
try:
    from config.database_render import engine, SessionLocal
    print("✅ database_render importado correctamente")

    # Test de conexión a la base de datos
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT version()")
            version = result.fetchone()[0]
            print(f"✅ Conexión a PostgreSQL exitosa: {version[:50]}...")
    except Exception as e:
        print(f"⚠️ No se pudo conectar a la base de datos: {e}")

except Exception as e:
    print(f"❌ Error al importar o conectar a la base de datos: {e}")
    traceback.print_exc()

# Estado actual
print("\n📌 Estado actual:")
print(f"- Directorio de trabajo: {os.getcwd()}")
print(f"- DATABASE_URL configurada: {'Sí' if os.environ.get('DATABASE_URL') else 'No'}")
