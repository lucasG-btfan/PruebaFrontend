#!/usr/bin/env python3
"""
Production server runner for FastAPI application on Render.
This script runs Uvicorn with optimized settings for Render's environment.
"""
import os
import sys
import platform

print(f"🚀 Starting production server on {platform.system()}...")

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Configurar variable de entorno para producción
os.environ.setdefault("DATABASE_URL", os.getenv("DATABASE_URL", ""))

# Importar desde database_render
try:
    from config.database_render import create_tables, check_connection
    print("✅ Database module imported successfully")
except ImportError as e:
    print(f"❌ Error importing database module: {e}")
    print(f"📁 Current directory: {current_dir}")
    print(f"📁 Files in config directory: {os.listdir(os.path.join(current_dir, 'config')) if os.path.exists(os.path.join(current_dir, 'config')) else 'Config directory not found'}")
    sys.exit(1)

if __name__ == "__main__":
    # Verificar conexión a la base de datos primero
    print("🔍 Checking database connection...")
    if not check_connection():
        print("❌ Database connection failed!")
        sys.exit(1)

    print("✅ Database connection established")

    # Crear tablas de la base de datos antes de iniciar el servidor
    print("🔨 Creating database tables if needed...")
    if not create_tables():
        print("⚠️ Warning: Could not create tables (they may already exist)\n")

    # Configuración del servidor
    port = int(os.getenv("PORT", 8000))
    workers = int(os.getenv("WORKERS", 1))

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  🚀 FastAPI E-commerce - Optimized for Render Production  ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"📊 Configuration:")
    print(f"  • Host: 0.0.0.0")
    print(f"  • Port: {port}")
    print(f"  • Workers: {workers} (Render Free only supports 1 worker)")
    print(f"  • Backlog: 2048 pending connections")
    print(f"  • Max concurrency: 100 requests")
    print(f"  • Keep-alive timeout: 30s")
    print("🔥 Optimized for Render's environment")
    print(f"🌍 Starting FastAPI server on port {port}...\n")

    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            workers=workers,
            timeout_keep_alive=30,
            limit_concurrency=100,
            limit_max_requests=1000,
            backlog=2048,
            log_level="info",
            access_log=True,
        )
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("📦 Installing missing dependencies...")
        os.system("pip install uvicorn[standard]")
        print("🔄 Retrying...")
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            workers=workers,
            timeout_keep_alive=30,
            limit_concurrency=100,
            limit_max_requests=1000,
            backlog=2048,
            log_level="info",
            access_log=True,
        )
