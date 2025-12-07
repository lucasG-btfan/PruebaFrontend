# check_render.py 
import os
import sys

print("🔍 Render Environment Check")
print("=" * 50)

# 1. Variables de entorno
print("\n1. Environment Variables:")
print(f"   RENDER: {os.getenv('RENDER', 'NOT SET')}")
print(f"   PORT: {os.getenv('PORT', 'NOT SET')}")
print(f"   DATABASE_URL: {'SET' if os.getenv('DATABASE_URL') else 'NOT SET'}")
if os.getenv('DATABASE_URL'):
    db_url = os.getenv('DATABASE_URL')
    print(f"   DB URL starts with: {db_url[:30]}...")

# 2. Python y dependencias
print("\n2. Python Environment:")
print(f"   Python version: {sys.version}")
print(f"   Executable: {sys.executable}")

# 3. Probar imports básicos
print("\n3. Testing imports:")
try:
    import fastapi
    print(f"   ✅ FastAPI: {fastapi.__version__}")
except ImportError as e:
    print(f"   ❌ FastAPI: {e}")

try:
    import sqlalchemy
    print(f"   ✅ SQLAlchemy: {sqlalchemy.__version__}")
except ImportError as e:
    print(f"   ❌ SQLAlchemy: {e}")

try:
    import psycopg2
    print(f"   ✅ psycopg2: OK")
except ImportError as e:
    print(f"   ❌ psycopg2: {e}")

# 4. Verificar estructura
print("\n4. Directory structure:")
for root, dirs, files in os.walk("."):
    level = root.replace(".", "").count(os.sep)
    indent = " " * 2 * level
    print(f"{indent}{os.path.basename(root)}/")
    subindent = " " * 2 * (level + 1)
    for file in files[:5]:  # Solo primeros 5 archivos
        if file.endswith(".py"):
            print(f"{subindent}{file}")
    if len(files) > 5:
        print(f"{subindent}... and {len(files)-5} more")
    break  # Solo nivel raíz

print("\n" + "=" * 50)
print("✅ Check complete")