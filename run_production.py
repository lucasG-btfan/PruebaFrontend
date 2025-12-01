#!/usr/bin/env python3
"""
Production server runner for FastAPI application on Render.
This script runs Uvicorn with optimized settings for Render's environment.
"""
import os
import uvicorn
from config.database import create_tables
from main import app

# Configurar variable de entorno para producción
os.environ.setdefault("DATABASE_URL", os.getenv("DATABASE_URL", ""))

if __name__ == "__main__":
    # Crear tablas de la base de datos antes de iniciar el servidor
    print("📦 Creating database tables...")
    try:
        create_tables()
        print("✅ Database tables created successfully\n")
    except Exception as e:
        print(f"⚠️ Database tables may already exist or error occurred: {e}\n")

    # Configuración del servidor
    port = int(os.getenv("PORT", 8000))

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  🚀 FastAPI E-commerce - Optimized for Render Production  ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"📊 Configuration:")
    print(f"  • Host: 0.0.0.0")
    print(f"  • Port: {port}")
    print(f"  • Workers: 1 (Render Free only supports 1 worker)")
    print(f"  • Backlog: 2048 pending connections")
    print(f"  • Max concurrency: 100 requests")
    print(f"  • Keep-alive timeout: 30s")
    print("🔥 Optimized for Render's environment")
    print("Starting server...\n")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        # Configuraciones optimizadas para Render
        workers=1,  # Render Free solo soporta 1 worker
        timeout_keep_alive=30,
        limit_concurrency=100,
        limit_max_requests=1000,
        backlog=2048,
        log_level="info",
        access_log=True,
    )