#!/usr/bin/env python3
"""
Entry point mínimo para Render - SOLO inicia el servidor
"""
import os

if __name__ == "__main__":
    # Forzar configuración para Render
    os.environ.setdefault("RENDER", "true")
    
    import uvicorn
    
    port = int(os.getenv("PORT", "10000"))
    print(f"🚀 Starting FastAPI on port {port}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info",
        access_log=True
    )