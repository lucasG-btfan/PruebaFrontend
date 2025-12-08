# test_connection_fixed.py
import psycopg2

print("🔗 Probando conexión a Render PostgreSQL...")

try:
    conn = psycopg2.connect(
        host='dpg-d4mvsm1r0fns73ai8s10-a.ohio-postgres.render.com',
        database='ecommerce_db_sbeb',
        user='ecommerce_user',
        password='XuchJ7YFaWcfTnq4s1RX4CpTTGrxwfbG',
        sslmode='require'  # ✅ CRÍTICO para Render
    )
    
    cursor = conn.cursor()
    
    # 1. Verificar versión
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"✅ PostgreSQL: {version[0]}")
    
    # 2. Listar tablas
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;")
    tables = cursor.fetchall()
    print(f"\n📊 Tablas encontradas ({len(tables)}):")
    for table in tables:
        print(f"  - {table[0]}")
    
    # 3. Verificar datos de prueba en clients
    cursor.execute("SELECT COUNT(*) FROM clients;")
    count = cursor.fetchone()[0]
    print(f"\n👥 Clientes en tabla: {count}")
    
    cursor.close()
    conn.close()
    print("\n🎉 ¡Conexión exitosa con SSL!")
    
except Exception as e:
    print(f"❌ Error: {e}")