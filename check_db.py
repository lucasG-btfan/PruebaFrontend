# check_db.py
import os

# Configurar variable de entorno
os.environ['DATABASE_URL'] = 'postgresql://ecommerce_db_pg18_user:8wj5MwKBGSfrK3ZG6vADvjT5pkc4ai7u@dpg-d4riokmr433s73a9vb70-a.ohio-postgres.render.com/ecommerce_db_pg18'

from sqlalchemy import create_engine, text

engine = create_engine(os.environ['DATABASE_URL'])

try:
    with engine.connect() as conn:
        # Verificar versión de PostgreSQL
        result = conn.execute(text('SELECT version()'))
        print(f'✅ PostgreSQL: {result.scalar()}')
        
        # Listar tablas
        result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = [row[0] for row in result]
        print(f'\n📊 Tablas encontradas ({len(tables)}):')
        for table in sorted(tables):
            print(f'  - {table}')
            
        # Verificar estructura de tablas importantes
        print('\n🔍 Estructura de tabla "clients":')
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'clients'
            ORDER BY ordinal_position
        """))
        for col in result:
            print(f'  - {col[0]}: {col[1]} ({col[2]})')
            
except Exception as e:
    print(f'❌ Error de conexión: {e}')