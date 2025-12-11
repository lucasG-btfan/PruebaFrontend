import os
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://ecommerce_db_pg18_user:8wj5MwKBGSfrK3ZG6vADvjT5pkc4ai7u@dpg-d4riokmr433s73a9vb70-a.ohio-postgres.render.com/ecommerce_db_pg18"

engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})

with engine.connect() as conn:
    # Listar todas las tablas
    result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """))
    
    print("📊 Tablas en la base de datos:")
    for row in result:
        print(f"  - {row[0]}")
    
    # Verificar si hay alguna tabla
    result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
    count = result.scalar()
    print(f"\nTotal de tablas: {count}")