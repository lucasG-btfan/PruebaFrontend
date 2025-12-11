# test_connection.py
import os
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://ecommerce_db_pg18_user:8wj5MwKBGSfrK3ZG6vADvjT5pkc4ai7u@dpg-d4riokmr433s73a9vb70-a.ohio-postgres.render.com/ecommerce_db_pg18"

print("🔗 Probando conexión...")
try:
    engine = create_engine(
        DATABASE_URL, 
        connect_args={
            "sslmode": "require",
            "connect_timeout": 10
        }
    )
    
    with engine.connect() as conn:
        print("✅ ¡Conectado a PostgreSQL!")
        
        # Crear tabla clients simple
        print("\n🔨 Creando tabla clients...")
        
        sql = """
        CREATE TABLE IF NOT EXISTS clients (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            lastname VARCHAR(100) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            phone VARCHAR(20),
            company VARCHAR(100),
            tax_id VARCHAR(50),
            notes TEXT,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE,
            deleted_at TIMESTAMP WITH TIME ZONE
        );
        """
        
        conn.execute(text(sql))
        conn.commit()
        
        print("✅ Tabla 'clients' creada!")
        
        # Verificar
        result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        print("\n📊 Tablas existentes:")
        for row in result:
            print(f"  - {row[0]}")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()