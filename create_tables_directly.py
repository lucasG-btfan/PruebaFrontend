# create_tables_directly.py
import os
import sys
import traceback

# Añadir el directorio actual al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar variable de entorno para database_render
os.environ['DATABASE_URL'] = 'postgresql://ecommerce_db_pg18_user:8wj5MwKBGSfrK3ZG6vADvjT5pkc4ai7u@dpg-d4riokmr433s73a9vb70-a.ohio-postgres.render.com/ecommerce_db_pg18'

try:
    # Importar después de configurar la variable
    from config.database_render import create_tables, check_connection

    print("🔍 Verificando conexión a base de datos...")
    if check_connection():
        print("✅ Conexión exitosa")
        print("🔨 Creando tablas...")
        if create_tables():
            print("✅ Tablas creadas exitosamente")
        else:
            print("❌ Error creando tablas")
    else:
        print("❌ No se pudo conectar a la base de datos")

except ImportError as e:
    print(f"❌ Error al importar módulos: {e}")
    traceback.print_exc()
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    traceback.print_exc()
