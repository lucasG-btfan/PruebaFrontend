# test_db_connection.py
"""
Probar conexión a la base de datos de Render.
"""
import os
from sqlalchemy import create_engine, text

# URL de Render
DATABASE_URL = "postgresql://ecommerce_user:XuchJ7YFaWcfTnq4s1RX4CpTTGrxwfbG@dpg-d4mvsm1r0fns73ai8s10-a.ohio-postgres.render.com/ecommerce_db_sbeb"

print("🔗 Probando conexión a Render...")
print(f"URL: {DATABASE_URL[:60]}...")

try:
    # Crear engine
    engine = create_engine(DATABASE_URL, echo=True)
    
    # Probar conexión
    with engine.connect() as conn:
        # Ejecutar consulta simple
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"✅ PostgreSQL versión: {version}")
        
        # Verificar si hay tablas
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        
        tables = [row[0] for row in result.fetchall()]
        if tables:
            print(f"📋 Tablas existentes ({len(tables)}):")
            for table in tables:
                print(f"  • {table}")
        else:
            print("📋 No hay tablas en la base de datos.")
            
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    print("\n🔍 Soluciones posibles:")
    print("1. Verifica que la base de datos esté activa en Render")
    print("2. Verifica el usuario y contraseña")
    print("3. Asegúrate de que no haya problemas de firewall")