# test_render_connection.py
"""
Prueba específica para conexión a Render.
"""
import psycopg2
from urllib.parse import urlparse

# Tu URL de Render
database_url = "postgresql://ecommerce_db_pg18_user:8wj5MwKBGSfrK3ZG6vADvjT5pkc4ai7u@dpg-d4riokmr433s73a9vb70-a.ohio-postgres.render.com/ecommerce_db_pg18"

print("🧪 Probando conexión directa a Render con psycopg2...")

try:
    # Parsear la URL
    result = urlparse(database_url)
    
    # Conectar
    conn = psycopg2.connect(
        host=result.hostname,
        port=result.port,
        database=result.path[1:],  # Quitar el '/'
        user=result.username,
        password=result.password,
        sslmode='require'  # Render requiere SSL
    )
    
    print("✅ ¡CONEXIÓN EXITOSA!")
    
    # Crear cursor
    cur = conn.cursor()
    
    # Ejecutar consulta
    cur.execute("SELECT version();")
    version = cur.fetchone()[0]
    print(f"PostgreSQL: {version}")
    
    # Cerrar
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n🔍 Posibles soluciones:")
    print("1. Verifica que la base de datos esté activa en render.com")
    print("2. Asegúrate de que el usuario 'ecommerce_user' tenga permisos")
    print("3. Verifica la contraseña")
    print("4. Render requiere SSL, asegúrate de usar sslmode='require'")