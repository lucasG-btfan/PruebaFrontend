# verify_all.py
print("🔍 Verificando configuración completa...\n")

# 1. Verificar variable de entorno
import os
os.environ['DATABASE_URL'] = 'postgresql://ecommerce_user:XuchJ7YFaWcfTnq4s1RX4CpTTGrxwfbG@dpg-d4mvsm1r0fns73ai8s10-a.ohio-postgres.render.com/ecommerce_db_sbeb'

print("1. Variable DATABASE_URL:", os.environ.get('DATABASE_URL', 'NOT SET')[:50] + "...")

# 2. Verificar imports de modelos
print("\n2. Probando imports de modelos...")
try:
    from models import ClientModel, BillModel
    print("   ✅ Modelos importados correctamente")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 3. Verificar config
print("\n3. Probando config...")
try:
    from config import engine, SessionLocal
    print("   ✅ Config importado correctamente")
    
    # Verificar engine
    if engine:
        print("   ✅ Engine está definido")
        
        # Probar conexión
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("   ✅ Conexión a DB exitosa")
    else:
        print("   ❌ Engine es None")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n🎯 Si todo está OK, puedes ejecutar:")
print("   python test_server.py")