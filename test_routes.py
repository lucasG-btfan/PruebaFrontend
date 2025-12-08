# test_routes.py
import sys
sys.path.append('.')  # Agrega el directorio actual al path

from main import app

print("📋 RUTAS DISPONIBLES EN EL BACKEND:")
print("=" * 50)

for route in app.routes:
    if hasattr(route, 'methods'):
        methods = ', '.join(route.methods) if route.methods else 'GET'
        print(f"{methods:10} {route.path}")