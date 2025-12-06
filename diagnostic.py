# diagnostic.py
import os
import sys

print("🔍 DIAGNÓSTICO DEL SISTEMA")
print("=" * 50)

print("\n1️⃣ VARIABLES DE ENTORNO:")
print(f"   DATABASE_URL: {'✅ Configurada' if 'DATABASE_URL' in os.environ else '❌ No configurada'}")
print(f"   PORT: {os.environ.get('PORT', '❌ No configurado')}")
print(f"   Directorio: {os.getcwd()}")

print("\n2️⃣ ARCHIVOS CRÍTICOS:")
files = [
    'models/base_model.py',
    'main.py',
    'config/database_render.py',
    'run_simple.py'
]
for file in files:
    exists = os.path.exists(file)
    print(f"   {file}: {'✅ Existe' if exists else '❌ No existe'}")

print("\n3️⃣ IMPORTACIONES BÁSICAS:")
try:
    import sqlalchemy
    print(f"   SQLAlchemy: ✅ v{sqlalchemy.__version__}")
except:
    print(f"   SQLAlchemy: ❌")

try:
    import fastapi
    print(f"   FastAPI: ✅ v{fastapi.__version__}")
except:
    print(f"   FastAPI: ❌")

# 4. Corregir base_model si es necesario
print("\n4️⃣ CORRECCIÓN BASE_MODEL:")
if os.path.exists('models/base_model.py'):
    with open('models/base_model.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'from sqlalchemy import Integer' not in content:
            print("   ⚠️ Necesita corrección (ejecuta fix_base_model.py)")
        else:
            print("   ✅ Ya está corregido")
else:
    print("   ❌ No existe base_model.py")

print("\n" + "=" * 50)
print("🎯 RECOMENDACIONES:")
print("1. Ejecutar: python fix_base_model.py")
print("2. Ejecutar: python create_tables_directly.py")
print("3. Ejecutar: python run_simple.py")