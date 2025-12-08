# diagnose.py
import sys
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🔍 =============== DIAGNÓSTICO COMPLETO ===============")

# 1. Verificar variables de entorno
print("\n1️⃣ VERIFICANDO VARIABLES DE ENTORNO:")
database_url = os.getenv("DATABASE_URL")
print(f"   DATABASE_URL: {'✅ Seteada' if database_url else '❌ No set'}")
if database_url:
    print(f"   Longitud: {len(database_url)} caracteres")
    print(f"   Inicia con: {database_url[:30]}...")

# 2. Probar importación de config
print("\n2️⃣ VERIFICANDO IMPORTACIÓN DE CONFIG:")
try:
    from config import engine, DATABASE_URL, check_connection, Base
    print("   ✅ Config importada correctamente")
    print(f"   Base class: {Base}")
    print(f"   Engine: {engine}")
except Exception as e:
    print(f"   ❌ Error importando config: {e}")
    import traceback
    traceback.print_exc()

# 3. Probar conexión a DB
print("\n3️⃣ VERIFICANDO CONEXIÓN A BASE DE DATOS:")
try:
    success = check_connection()
    if success:
        print("   ✅ Conexión exitosa a PostgreSQL")
    else:
        print("   ❌ Falló la conexión a la base de datos")
except Exception as e:
    print(f"   ❌ Error en check_connection: {e}")

# 4. Verificar modelos
print("\n4️⃣ VERIFICANDO MODELOS:")
try:
    from models.base_model import Base as ModelsBase
    print(f"   ✅ Base desde models: {ModelsBase}")
    
    # Verificar que es la misma Base
    from config import Base as ConfigBase
    if ModelsBase is ConfigBase:
        print("   ✅ Misma instancia de Base en config y models")
    else:
        print("   ⚠️ Diferentes instancias de Base")
        
    # Listar modelos registrados
    if hasattr(ModelsBase, 'registry'):
        registered = list(ModelsBase.registry._class_registry.keys())
        print(f"   📋 Modelos registrados: {registered}")
        
except Exception as e:
    print(f"   ❌ Error con modelos: {e}")

# 5. Verificar estructura de tablas
print("\n5️⃣ VERIFICANDO METADATA DE TABLAS:")
try:
    from config import Base
    tables = Base.metadata.tables.keys()
    if tables:
        print(f"   ✅ Tablas en metadata: {list(tables)}")
    else:
        print("   ⚠️ No hay tablas en metadata (¿modelos no importados?)")
except Exception as e:
    print(f"   ❌ Error con metadata: {e}")

print("\n🔍 =============== FIN DEL DIAGNÓSTICO ===============")