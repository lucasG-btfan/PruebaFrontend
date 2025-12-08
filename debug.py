import os
print("Variables de entorno:")
print(f"PORT: {os.getenv('PORT')}")
print(f"RENDER: {os.getenv('RENDER')}")
print(f"CORS_ORIGINS: {os.getenv('CORS_ORIGINS')}")