#!/usr/bin/env python3
"""
Production server runner for high-concurrency FastAPI application.
This script runs Uvicorn with multiple workers to handle 400+ concurrent requests.
"""
import multiprocessing
import os
import uvicorn
from config.database import create_tables

# Import the app instance directly from main
from main import app

# Calculate optimal workers based on CPU cores
CPU_COUNT = multiprocessing.cpu_count()
DEFAULT_WORKERS = min(max(2 * CPU_COUNT + 1, 4), 8)  # Between 4-8 workers

# Configuration from environment variables
WORKERS = int(os.getenv('UVICORN_WORKERS', DEFAULT_WORKERS))
HOST = os.getenv('API_HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8000))
RELOAD = os.getenv('RELOAD', 'false').lower() == 'true'

# Performance tuning
BACKLOG = int(os.getenv('BACKLOG', '2048'))  # Pending connections queue
TIMEOUT_KEEP_ALIVE = int(os.getenv('TIMEOUT_KEEP_ALIVE', '5'))
LIMIT_CONCURRENCY = int(os.getenv('LIMIT_CONCURRENCY', '1000'))
LIMIT_MAX_REQUESTS = int(os.getenv('LIMIT_MAX_REQUESTS', '10000'))

if __name__ == "__main__":
    # Create database tables before starting server
    print("📦 Creating database tables...")
    try:
        create_tables()
        print("✅ Database tables created successfully\n")
    except Exception as e:
        print(f"⚠️  Database tables may already exist or error occurred: {e}\n")

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  🚀 FastAPI E-commerce - High Performance Production Mode  ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"📊 Configuration:")
    print(f"  • Workers: {WORKERS} (CPU cores: {CPU_COUNT})")
    print(f"  • Host: {HOST}")
    print(f"  • Port: {PORT}")
    print(f"  • Backlog: {BACKLOG} pending connections")
    print(f"  • Max concurrency: {LIMIT_CONCURRENCY} requests")
    print(f"  • Keep-alive timeout: {TIMEOUT_KEEP_ALIVE}s")
    print("🔥 Optimized for ~400 concurrent requests")
    print(f"💾 Database pool: 50 connections + 100 overflow per worker")
    print(f"⚡ Total capacity: ~{WORKERS * 150} database connections")
    print("Starting server...\n")

    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        workers=WORKERS,
        reload=RELOAD,
        # Performance optimizations
        backlog=BACKLOG,
        timeout_keep_alive=TIMEOUT_KEEP_ALIVE,
        limit_concurrency=LIMIT_CONCURRENCY,
        limit_max_requests=LIMIT_MAX_REQUESTS,
        # Logging
        access_log=True,
        log_level="info",
    )
