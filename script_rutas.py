import uvicorn
from main import app

# Listar todas las rutas
print("📋 RUTAS REGISTRADAS:")
for route in app.routes:
    if hasattr(route, "path"):
        methods = route.methods if hasattr(route, "methods") else ["ANY"]
        print(f"  {','.join(methods)} {route.path}")