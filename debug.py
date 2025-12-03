# debug.py
import uvicorn
import sys
import traceback

try:
    print("🚀 Iniciando backend en modo debug...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )
except Exception as e:
    print(f"❌ Error fatal: {e}")
    traceback.print_exc()
    input("Presiona Enter para continuar...")