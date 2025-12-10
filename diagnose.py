# diagnose.py
import os
import sys

print("🔍 Diagnóstico del sistema")

# 1. Verificar estructura de directorios
print("\n1. Estructura de directorios:")
for root, dirs, files in os.walk("."):
    level = root.replace(".", "").count(os.sep)
    indent = " " * 2 * level
    print(f"{indent}{os.path.basename(root)}/")
    subindent = " " * 2 * (level + 1)
    for file in files:
        if file.endswith(".py"):
            print(f"{subindent}{file}")

# 2. Verificar models/client.py
print("\n2. Contenido de models/client.py:")
try:
    with open("models/client.py", "r") as f:
        content = f.read()
        # Buscar class definition
        import re
        match = re.search(r"class\s+(\w+)", content)
        if match:
            print(f"   Clase encontrada: {match.group(1)}")
        else:
            print("   ❌ No se encontró definición de clase")
        
        # Verificar BaseModel import
        if "from models.base_model import BaseModel" in content:
            print("   ✅ BaseModel importado correctamente")
        else:
            print("   ❌ BaseModel no importado")
            
except FileNotFoundError:
    print("   ❌ models/client.py no existe")
    # Verificar si existe con otro nombre
    py_files = [f for f in os.listdir("models") if f.endswith(".py")]
    print(f"   Archivos en models/: {py_files}")

# 3. Verificar __init__.py en models
print("\n3. models/__init__.py:")
try:
    with open("models/__init__.py", "r") as f:
        print(f.read())
except FileNotFoundError:
    print("   ⚠️ No existe models/__init__.py")

print("\n✅ Diagnóstico completado")