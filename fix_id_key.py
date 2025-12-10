from config.database import SessionLocal, engine
from models.client import ClientModel
from sqlalchemy import text

def fix_id_key_column():
    """Agrega la columna id_key a la tabla clients si no existe"""
    db = SessionLocal()
    try:
        # Verificar si la columna id_key existe
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'clients' 
            AND column_name = 'id_key'
        """))
        
        if not result.fetchone():
            print("Agregando columna id_key a tabla clients...")
            # Agregar columna id_key
            db.execute(text("ALTER TABLE clients ADD COLUMN id_key INTEGER UNIQUE"))
            
            # Poblar id_key con valores de id
            db.execute(text("UPDATE clients SET id_key = id"))
            
            # Hacer que id_key no sea null
            db.execute(text("ALTER TABLE clients ALTER COLUMN id_key SET NOT NULL"))
            
            db.commit()
            print("✅ Columna id_key agregada exitosamente")
        else:
            print("✅ La columna id_key ya existe")
            
        # Verificar datos
        clients = db.query(ClientModel).all()
        for client in clients:
            if client.id_key is None:
                client.id_key = client.id
        db.commit()
        print("✅ Valores de id_key actualizados")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_id_key_column()