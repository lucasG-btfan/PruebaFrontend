"""
Simple server runner for testing.
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables if not set
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "postgresql://ecommerce_user:XuchJ7YFaWcfTnq4s1RX4CpTTGrxwfbG@dpg-d4mvsm1r0fns73ai8s10-a.ohio-postgres.render.com/ecommerce_db_sbeb"
if "PORT" not in os.environ:
    os.environ["PORT"] = "8000"

print(f"🔗 Database URL: {os.environ['DATABASE_URL'][:50]}...")
print(f"🌐 Port: {os.environ['PORT']}")

# Import and run
from main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ["PORT"]),
        log_level="info"
    )