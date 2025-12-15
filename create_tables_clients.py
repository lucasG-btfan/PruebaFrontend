# create_clients_table.py
import os
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://ecommerce_db_pg18_user:8wj5MwKBGSfrK3ZG6vADvjT5pkc4ai7u@dpg-d4riokmr433s73a9vb70-a.ohio-postgres.render.com/ecommerce_db_pg18"

sql = """
-- Tabla clients
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

-- Tabla addresses
CREATE TABLE IF NOT EXISTS addresses (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id),
    street VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'Argentina',
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insertar datos de prueba
INSERT INTO clients (name, lastname, email, phone) 
VALUES 
    ('Juan', 'Pérez', 'juan@example.com', '123456789'),
    ('María', 'Gómez', 'maria@example.com', '987654321')
ON CONFLICT (email) DO NOTHING;

SELECT '✅ Tablas creadas y datos insertados' as resultado;
"""

print("🔨 Creando tablas...")
engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})

try:
    with engine.connect() as conn:
        # Ejecutar cada statement por separado
        statements = sql.split(';')
        
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                print(f"Ejecutando: {stmt[:50]}...")
                conn.execute(text(stmt))
        
        conn.commit()
        print("✅ ¡Tablas creadas exitosamente!")
        
except Exception as e:
    print(f"❌ Error: {e}")