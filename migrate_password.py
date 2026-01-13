import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Usar SQL directo en Render
import psycopg2
from urllib.parse import urlparse
import hashlib
import base64
import secrets

def get_render_db_url():
    """Obtener URL de la base de datos de Render"""
    # Opción 1: Variable de entorno de Render
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        # Opción 2: Pedir manualmente
        print("⚠️ DATABASE_URL no encontrado en variables de entorno")
        database_url = input("Introduce la DATABASE_URL de Render: ").strip()
    
    return database_url

def migrate_all_passwords():
    database_url = get_render_db_url()
    if not database_url:
        print("❌ No se pudo obtener la URL de la base de datos")
        return

    print(f"🔗 Conectando a la base de datos...")

    try:
        result = urlparse(database_url)

        # Determinar si es local o producción
        is_local = result.hostname in ['localhost', '127.0.0.1']
        ssl_mode = 'disable' if is_local else 'require'

        conn = psycopg2.connect(
            host=result.hostname,
            port=result.port,
            database=result.path[1:],
            user=result.username,
            password=result.password,
            sslmode=ssl_mode  # Usa SSL solo si no es local
        )

        cursor = conn.cursor()

        # 1. Asegurar que el cliente con id_key=0 tenga la contraseña coleMC_89
        cursor.execute("""
            SELECT password_hash, password_salt
            FROM clients
            WHERE id_key = 0
        """)
        admin_data = cursor.fetchone()

        if admin_data:
            old_admin_hash, old_admin_salt = admin_data
            salt_bytes = secrets.token_bytes(32)
            new_admin_salt = base64.b64encode(salt_bytes).decode('utf-8')
            new_admin_hash = hashlib.pbkdf2_hmac(
                'sha256',
                "coleMC_89".encode('utf-8'),
                salt_bytes,
                100000,
                dklen=32
            ).hex()

            if old_admin_hash != new_admin_hash:
                cursor.execute("""
                    UPDATE clients
                    SET password_hash = %s, password_salt = %s
                    WHERE id_key = 0
                """, (new_admin_hash, new_admin_salt))
                print(f"🔒 Contraseña del cliente con id_key=0 actualizada a coleMC_89")
            else:
                print(f"🔒 Contraseña del cliente con id_key=0 ya es coleMC_89")
        else:
            print(f"⚠️ No se encontró el cliente con id_key=0")

        # 2. Migrar el resto de usuarios (id_key != 0)
        cursor.execute("""
            SELECT id_key, email, password_hash, password_salt
            FROM clients
            WHERE id_key != 0
            ORDER BY id_key
        """)

        users = cursor.fetchall()
        print(f"📊 Encontrados {len(users)} usuarios para migrar")

        migrated_count = 0
        failed_count = 0

        for user_id, email, old_hash, old_salt in users:
            try:
                print(f"\n🔍 Procesando usuario {user_id}: {email}")
                new_password = "password123"
                salt_bytes = secrets.token_bytes(32)
                new_salt = base64.b64encode(salt_bytes).decode('utf-8')
                new_hash = hashlib.pbkdf2_hmac(
                    'sha256',
                    new_password.encode('utf-8'),
                    salt_bytes,
                    100000,
                    dklen=32
                ).hex()

                cursor.execute("""
                    UPDATE clients
                    SET password_hash = %s, password_salt = %s
                    WHERE id_key = %s
                """, (new_hash, new_salt, user_id))
                migrated_count += 1
                print(f"  ✅ Usuario {email} migrado")

            except Exception as e:
                failed_count += 1
                print(f"  ❌ Error migrando usuario {email}: {e}")

        conn.commit()
        print(f"\n{'='*50}")
        print(f"📋 RESUMEN DE MIGRACIÓN:")
        print(f"  ✅ Migrados exitosamente: {migrated_count}")
        print(f"  ❌ Fallidos: {failed_count}")
        print(f"{'='*50}")

        cursor.close()
        conn.close()
        print(f"\n🎉 ¡Migración completada!")
        print(f"💡 Nota: Ahora todos los usuarios (excepto id_key=0) pueden iniciar sesión con 'password123'")

    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print(f"💡 Asegúrate de que la DATABASE_URL sea correcta y el servidor PostgreSQL esté en ejecución.")


if __name__ == "__main__":
    migrate_all_passwords()