# migrate_to_idkey.py
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import time

# Configuración
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL no configurada")
    sys.exit(1)

def log_step(message):
    print(f"\n{'='*60}")
    print(f"STEP: {message}")
    print('='*60)

def migrate_to_idkey():
    """Migración completa a id_key"""
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # PASO 0: Backup mental
        log_step("0. Verificando estado actual")
        
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
            # Agregar columna
            session.execute(text("ALTER TABLE clients ADD COLUMN id_key INTEGER"))
            
            # Copiar valores de id a id_key
            session.execute(text("UPDATE clients SET id_key = id"))
            
            # Hacerla NOT NULL y UNIQUE
            session.execute(text("ALTER TABLE clients ALTER COLUMN id_key SET NOT NULL"))
            session.execute(text("ALTER TABLE clients ADD CONSTRAINT unique_id_key UNIQUE (id_key)"))
            session.commit()
            print("✅ Columna id_key creada y poblada")
        else:
            print("✅ Columna id_key ya existe")
        
        # PASO 2: Verificar y actualizar tablas relacionadas
        log_step("2. Actualizando tablas relacionadas")
        
        # Lista de tablas que referencian clients
        related_tables = ['addresses', 'orders', 'bills']
        
        for table in related_tables:
            # Verificar estructura
            result = session.execute(text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table}' 
                AND column_name IN ('client_id', 'client_id_key')
            """))
            
            columns = [row[0] for row in result]
            
            if 'client_id_key' in columns:
                print(f"✅ {table} ya tiene client_id_key")
            elif 'client_id' in columns:
                print(f"🔄 Renombrando client_id a client_id_key en {table}")
                
                # Renombrar columna
                session.execute(text(f"""
                    ALTER TABLE {table} 
                    RENAME COLUMN client_id TO client_id_key
                """))
                
                # Actualizar ForeignKey constraint
                try:
                    # Eliminar constraint vieja si existe
                    session.execute(text(f"""
                        ALTER TABLE {table}
                        DROP CONSTRAINT IF EXISTS {table}_client_id_fkey
                    """))
                except:
                    pass
                
                # Crear nueva ForeignKey
                session.execute(text(f"""
                    ALTER TABLE {table}
                    ADD CONSTRAINT {table}_client_id_key_fkey 
                    FOREIGN KEY (client_id_key) 
                    REFERENCES clients(id_key)
                """))
                
                session.commit()
                print(f"✅ {table} actualizada")
            else:
                print(f"⚠️  {table} no tiene columna de referencia a client")
        
        # PASO 3: Hacer id_key la primary key de clients
        log_step("3. Configurando id_key como primary key")
        
        # Verificar si id_key ya es PK
        result = session.execute(text("""
            SELECT c.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.constraint_column_usage ccu 
              ON tc.constraint_name = ccu.constraint_name
            JOIN information_schema.columns c 
              ON c.table_name = ccu.table_name 
              AND c.column_name = ccu.column_name
            WHERE tc.table_name = 'clients' 
              AND tc.constraint_type = 'PRIMARY KEY'
        """))
        
        pk_column = result.fetchone()
        
        if pk_column and pk_column[0] == 'id_key':
            print("✅ id_key ya es primary key")
        else:
            print("🔄 Cambiando primary key a id_key")
            
            # Si hay una PK existente, eliminarla
            session.execute(text("""
                ALTER TABLE clients 
                DROP CONSTRAINT IF EXISTS clients_pkey
            """))
            
            # Establecer nueva PK
            session.execute(text("""
                ALTER TABLE clients 
                ADD PRIMARY KEY (id_key)
            """))
            
            session.commit()
            print("✅ Primary key cambiada a id_key")
        
        # PASO 4: Actualizar secuencia si es necesario (PostgreSQL)
        log_step("4. Actualizando secuencias")
        
        # Verificar si hay una secuencia para id_key
        result = session.execute(text("""
            SELECT setval(pg_get_serial_sequence('clients', 'id_key'), 
                   COALESCE(MAX(id_key), 1))
            FROM clients
        """))
        
        print("✅ Secuencias actualizadas")
        
        # PASO 5: Validación final
        log_step("5. Validando migración")
        
        # Contar clients
        result = session.execute(text("SELECT COUNT(*) FROM clients"))
        client_count = result.fetchone()[0]
        print(f"📊 Total clients: {client_count}")
        
        # Verificar consistencia
        result = session.execute(text("""
            SELECT COUNT(*) 
            FROM clients 
            WHERE id IS DISTINCT FROM id_key
        """))
        inconsistent = result.fetchone()[0]
        
        if inconsistent > 0:
            print(f"⚠️  {inconsistent} registros con id diferente a id_key")
            # Arreglar automáticamente
            session.execute(text("UPDATE clients SET id = id_key WHERE id IS DISTINCT FROM id_key"))
            session.commit()
            print("✅ Inconsistencias corregidas")
        else:
            print("✅ Todos los registros son consistentes")
        
        print("\n" + "🎉" * 20)
        print("MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("🎉" * 20)
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ ERROR durante migración: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        session.close()

if __name__ == "__main__":
    print("🚀 INICIANDO MIGRACIÓN A id_key")
    print("⏰ Este proceso puede tardar unos minutos...")
    
    # Confirmación
    confirm = input("\n⚠️  ¿Estás seguro de continuar? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Migración cancelada")
        sys.exit(0)
    
    success = migrate_to_idkey()
    
    if success:
        print("\n✅ Migración exitosa. Siguientes pasos:")
        print("1. Actualiza tus modelos Python para usar id_key")
        print("2. Actualiza serializers/schemas")
        print("3. Actualiza frontend para usar id_key")
        print("4. Elimina código obsoleto en la próxima release")
    else:
        print("\n❌ Migración falló. Revisa los logs.")
        sys.exit(1)