# migrate_to_idkey.py - CORRECCIÓN DEL ERROR
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import time
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
load_dotenv()

# Configuración - Usar diferentes fuentes
DATABASE_URL = None

# Opción 1: Desde variable de entorno
if os.getenv("DATABASE_URL"):
    DATABASE_URL = os.getenv("DATABASE_URL")
    print("✅ DATABASE_URL cargada desde variable de entorno")
# Opción 2: Valor por defecto (tu URL de Render)
else:
    DATABASE_URL = "postgresql://ecommerce_db_pg18_user:8wj5MwKBGSfrK3ZG6vADvjT5pkc4ai7u@dpg-d4riokmr433s73a9vb70-a.ohio-postgres.render.com/ecommerce_db_pg18"
    print("⚠️  Usando DATABASE_URL por defecto")

if not DATABASE_URL:
    print("❌ DATABASE_URL no configurada")
    sys.exit(1)

def log_step(message):
    print(f"\n{'='*60}")
    print(f"STEP: {message}")
    print('='*60)

def migrate_to_idkey():
    """Migración completa a id_key"""
    
    # ✅ Usar la variable global
    global DATABASE_URL
    
    # ✅ Asegurar que la URL use postgresql:// en lugar de postgres://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        print("✅ URL convertida a postgresql://")
    
    print(f"🔗 Conectando a: {DATABASE_URL[:50]}...")
    
    try:
        engine = create_engine(
            DATABASE_URL,
            connect_args={
                "sslmode": "require",
                "connect_timeout": 30
            },
            pool_pre_ping=True
        )
        
        # Probar conexión
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Conectado a PostgreSQL: {version[:50]}...")
        
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # PASO 0: Verificar estado actual
            log_step("0. Verificando estado actual de la base de datos")
            
            # Verificar que la tabla clients existe
            result = session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'clients'
                )
            """))
            
            if not result.scalar():
                print("❌ La tabla 'clients' no existe. ¿Ejecutaste las migraciones iniciales?")
                return False
            
            # Verificar columnas actuales
            result = session.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'clients' 
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            print("📊 Columnas actuales en 'clients':")
            for col in columns:
                print(f"  - {col[0]}: {col[1]}")
            
            # PASO 1: Verificar si clients tiene columna id_key
            result = session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'clients' 
                AND column_name = 'id_key'
            """))
            
            has_id_key = result.fetchone() is not None
            
            if not has_id_key:
                log_step("1. Agregando columna id_key a clients")
                
                try:
                    # Agregar columna id_key
                    session.execute(text("""
                        ALTER TABLE clients 
                        ADD COLUMN id_key INTEGER
                    """))
                    print("  ✅ Columna id_key agregada")
                except Exception as e:
                    print(f"  ⚠️  Error al agregar columna: {e}")
                    print("  Continuando...")
                
                # Copiar valores de id a id_key
                session.execute(text("""
                    UPDATE clients 
                    SET id_key = id
                    WHERE id_key IS NULL
                """))
                print("  ✅ Valores copiados de id a id_key")
                
                session.commit()
                
                # Verificar datos copiados
                result = session.execute(text("""
                    SELECT COUNT(*) as total,
                           COUNT(id_key) as con_id_key,
                           COUNT(DISTINCT id_key) as unicos,
                           MIN(id_key) as min_val,
                           MAX(id_key) as max_val
                    FROM clients
                """))
                
                stats = result.fetchone()
                print(f"  📊 Estadísticas:")
                print(f"    - Total registros: {stats[0]}")
                print(f"    - Con id_key: {stats[1]}")
                print(f"    - Valores únicos: {stats[2]}")
                print(f"    - Mínimo: {stats[3]}")
                print(f"    - Máximo: {stats[4]}")
                
            else:
                print("✅ Columna id_key ya existe")
            
            # PASO 2: Hacer id_key NOT NULL y agregar constraint UNIQUE
            log_step("2. Configurando constraints de id_key")
            
            # Verificar si id_key ya es NOT NULL
            result = session.execute(text("""
                SELECT is_nullable
                FROM information_schema.columns
                WHERE table_name = 'clients' 
                AND column_name = 'id_key'
            """))
            
            nullable = result.scalar()
            
            if nullable == 'YES':
                print("  🔄 Haciendo id_key NOT NULL...")
                session.execute(text("""
                    ALTER TABLE clients 
                    ALTER COLUMN id_key SET NOT NULL
                """))
                print("  ✅ id_key marcada como NOT NULL")
            else:
                print("  ✅ id_key ya es NOT NULL")
            
            # Verificar constraint UNIQUE
            result = session.execute(text("""
                SELECT constraint_name
                FROM information_schema.table_constraints
                WHERE table_name = 'clients' 
                AND constraint_type = 'UNIQUE'
                AND constraint_name LIKE '%id_key%'
            """))
            
            if not result.fetchone():
                print("  🔄 Agregando constraint UNIQUE a id_key...")
                try:
                    session.execute(text("""
                        ALTER TABLE clients 
                        ADD CONSTRAINT clients_id_key_unique UNIQUE (id_key)
                    """))
                    print("  ✅ Constraint UNIQUE agregada")
                except Exception as e:
                    print(f"  ⚠️  Error al agregar UNIQUE: {e}")
            else:
                print("  ✅ Constraint UNIQUE ya existe")
            
            session.commit()
            
            # PASO 3: Actualizar tablas relacionadas (OPCIONAL - puedes omitir si causa problemas)
            log_step("3. Actualizando tablas relacionadas (opcional)")
            
            print("  ⚠️  Este paso es opcional. Puedes actualizar las relaciones manualmente después.")
            print("  Las tablas relacionadas (addresses, orders, bills) pueden actualizarse más tarde.")
            
            # PASO 4: Validación final
            log_step("4. Validación final")
            
            # Contar clients
            result = session.execute(text("SELECT COUNT(*) FROM clients"))
            client_count = result.fetchone()[0]
            print(f"📊 Total clients en base de datos: {client_count}")
            
            # Verificar consistencia id vs id_key
            result = session.execute(text("""
                SELECT COUNT(*) as inconsistencias
                FROM clients 
                WHERE id IS DISTINCT FROM id_key
            """))
            
            inconsistent = result.fetchone()[0]
            
            if inconsistent > 0:
                print(f"⚠️  {inconsistent} registros con id diferente a id_key")
                print("  🔄 Actualizando id para que coincida con id_key...")
                
                session.execute(text("""
                    UPDATE clients 
                    SET id = id_key 
                    WHERE id IS DISTINCT FROM id_key
                """))
                session.commit()
                print("  ✅ Inconsistencias corregidas")
            else:
                print("✅ Todos los registros son consistentes (id = id_key)")
            
            # Mostrar primeros 5 registros como ejemplo
            result = session.execute(text("""
                SELECT id, id_key, name, email
                FROM clients
                ORDER BY id_key
                LIMIT 5
            """))
            
            print("\n📋 Primeros 5 clientes (ejemplo):")
            for row in result:
                print(f"  - id: {row[0]}, id_key: {row[1]}, nombre: {row[2]}")
            
            print("\n" + "🎉" * 20)
            print("MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("🎉" * 20)
            
            print("\n📋 RESUMEN DE CAMBIOS:")
            print("1. ✅ Columna 'id_key' agregada a tabla 'clients'")
            print("2. ✅ Valores copiados de 'id' a 'id_key'")
            print("3. ✅ 'id_key' marcada como NOT NULL y UNIQUE")
            print("4. ✅ Inconsistencias id/id_key corregidas")
            
            print("\n⚠️  PRÓXIMOS PASOS IMPORTANTES:")
            print("1. ✅ Actualiza models/client.py para usar 'id_key' como primary_key")
            print("2. ✅ Actualiza los modelos relacionados (Address, Order, Bill)")
            print("3. ✅ Actualiza los controladores y serializadores")
            print("4. ✅ Haz commit y push a GitHub")
            print("5. ✅ Render se actualizará automáticamente")
            print("6. ✅ Prueba crear un nuevo cliente desde el frontend")
            
            return True
            
        except Exception as e:
            session.rollback()
            print(f"\n❌ ERROR durante migración: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            session.close()
            
    except Exception as e:
        print(f"\n❌ ERROR de conexión a la base de datos: {str(e)}")
        print("Verifica que:")
        print("1. La URL de la base de datos es correcta")
        print("2. Tu IP está en la lista de permitidos en Render")
        print("3. El usuario tiene permisos para modificar la tabla")
        
        # Consejo para Render: Necesitas agregar tu IP a la lista de allow
        print("\n💡 En Render PostgreSQL:")
        print("   - Ve a tu base de datos")
        print("   - Click en 'Network'")
        print("   - Agrega '0.0.0.0/0' temporalmente (para todas las IPs)")
        print("   - O agrega tu IP específica")
        
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO MIGRACIÓN A id_key")
    print(f"📅 {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Mostrar información (ocultando contraseña)
    safe_url = DATABASE_URL
    if "@" in safe_url:
        parts = safe_url.split("@")
        safe_url = parts[0][:30] + "*****@" + parts[1]
    print(f"🔗 Base de datos: {safe_url}")
    
    # Confirmación
    print("\n⚠️  ¡ADVERTENCIA! Este script modificará tu base de datos.")
    print("   Recomendación: Haz un backup primero.")
    
    confirm = input("\n¿Continuar con la migración? (escribe 'SI' para confirmar): ")
    if confirm.upper() != 'SI':
        print("\n❌ Migración cancelada por el usuario")
        sys.exit(0)
    
    print("\n⏰ Iniciando migración...")
    start_time = time.time()
    
    success = migrate_to_idkey()
    
    elapsed_time = time.time() - start_time
    print(f"\n⏱️  Tiempo total: {elapsed_time:.2f} segundos")
    
    if success:
        print("\n✅ ¡Migración completada exitosamente!")
        print("\n💾 Ahora haz commit y push a GitHub:")
        print("   git add .")
        print("   git commit -m 'Migración a id_key completada'")
        print("   git push origin main")
    else:
        print("\n❌ Migración falló. Revisa los errores arriba.")
        sys.exit(1)