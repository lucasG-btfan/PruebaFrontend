import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from config.database import SessionLocal
from models.category import CategoryModel
from models.product import ProductModel
from models.client import ClientModel
from models.address import AddressModel
import hashlib
import base64
from datetime import datetime
from sqlalchemy import text 

def create_hash(password: str, salt: str = None):
    """Crear hash igual que AuthService"""
    if salt is None:
        salt = base64.b64encode(os.urandom(32)).decode('utf-8')
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return password_hash, salt

def update_database():
    print("🔄 Actualizando base de datos...")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # 1. OBTENER LOS IDs REALES DE LOS CLIENTES
        print("\n🔍 Obteniendo IDs de clientes...")
        clients = db.query(ClientModel).order_by(ClientModel.id_key).all()
        
        client_map = {}
        for client in clients:
            client_map[client.email] = client.id_key
            print(f"   {client.id_key}: {client.name} {client.lastname} ({client.email})")
        
        # 2. LIMPIAR DIRECCIONES EXISTENTES (opcional)
        print("\n🗑️  Limpiando direcciones existentes...")
        db.query(AddressModel).delete()
        db.commit()
        print("   ✅ Direcciones eliminadas")
        
        # 3. CREAR NUEVAS DIRECCIONES EN ORDEN CORRECTO
        print("\n📍 Creando nuevas direcciones...")
        
        addresses = [
            # Admin (id_key = 0)
            {
                "client_id_key": 0,
                "street": "Av. Principal #123",
                "city": "Ciudad Autónoma de Buenos Aires",
                "state": "Buenos Aires",
                "zip_code": "C1001"
            },
            # Juan Pérez
            {
                "client_id_key": client_map.get("juan.perez@example.com", 1),
                "street": "Calle Falsa 123",
                "city": "Rosario",
                "state": "Santa Fe",
                "zip_code": "S2000"
            },
            # María Gómez
            {
                "client_id_key": client_map.get("maria.gomez@example.com", 2),
                "street": "Av. Libertador 456",
                "city": "Córdoba",
                "state": "Córdoba",
                "zip_code": "X5000"
            },
            # Carlos López
            {
                "client_id_key": client_map.get("carlos.lopez@example.com", 3),
                "street": "Av. San Martín 789",
                "city": "Mendoza",
                "state": "Mendoza",
                "zip_code": "M5500"
            },
            # Polaco Levy (ÚLTIMO - id_key más alto)
            {
                "client_id_key": client_map.get("polacoLibertaLPM@gmail.com"),
                "street": "Pasaje de la Ribera s/n",
                "city": "El Puerto",  # Ciudad ficticia
                "state": "Buenos Aires",
                "zip_code": "B1648"
            }
        ]
        
        # Crear direcciones
        for addr_data in addresses:
            if addr_data["client_id_key"] is not None:
                address = AddressModel(**addr_data)
                db.add(address)
                client = db.query(ClientModel).get(addr_data["client_id_key"])
                print(f"   ✅ Dirección para: {client.name} {client.lastname}")
                print(f"      📍 {addr_data['street']}, {addr_data['city']}")
        
        db.commit()
        
        # 4. AGREGAR PLAYSTATION 5 (solo si no existe)
        print("\n🎮 Verificando/agregando PlayStation 5...")
        
        # Verificar si la categoría Electrónica existe
        electronics_category = db.query(CategoryModel).filter(
            CategoryModel.id_key == 2
        ).first()
        
        if not electronics_category:
            electronics_category = CategoryModel(
                id_key=2,
                name="Electrónica",
                description="Dispositivos electrónicos y gadgets"
            )
            db.merge(electronics_category)
            print("   ✅ Categoría Electrónica creada")
        
        # Verificar si PlayStation 5 ya existe
        existing_ps5 = db.query(ProductModel).filter(
            ProductModel.name.ilike("%playstation%5%")
        ).first()
        
        if not existing_ps5:
            ps5 = ProductModel(
                id_key=2,  # ID 2 para PlayStation 5
                name="PlayStation 5",
                price=1499999.00,
                stock=12,
                description="Consola de videojuegos de última generación con gráficos 4K, sonido 3D y carga ultrarrápida. Incluye control DualSense con retroalimentación háptica.",
                category_id=2,
                sku="PS5-DIGITAL-1TB",
                image_url="https://images.unsplash.com/photo-1622297845775-5ff3fef71d13?q=80&w=707&auto=format&fit=crop"
            )
            db.merge(ps5)
            print("   ✅ PlayStation 5 agregada")
            print(f"      💰 Precio: ${ps5.price:,.2f}")
            print(f"      📦 Stock: {ps5.stock} unidades")
        else:
            print("   ⚠️  PlayStation 5 ya existe en la base de datos")
            print(f"      ID: {existing_ps5.id_key}")
            print(f"      Stock actual: {existing_ps5.stock}")
        
        db.commit()
        
        # 5. RESUMEN FINAL
        print("\n" + "=" * 50)
        print("📊 RESUMEN ACTUALIZADO:")
        print("=" * 50)
        
        # Contar direcciones por cliente
        result = db.execute(text("""  # ✅ ASÍ ESTÁ BIEN
        SELECT c.id_key, c.name, c.lastname, COUNT(a.id_key) as direcciones
        FROM clients c
        LEFT JOIN addresses a ON c.id_key = a.client_id_key
        GROUP BY c.id_key, c.name, c.lastname
        ORDER BY c.id_key
        """))
        
        print("\n👥 CLIENTES Y SUS DIRECCIONES:")
        for row in result:
            print(f"   #{row[0]}: {row[1]} {row[2]} - {row[3]} dirección(es)")
        
        # Mostrar productos
        print("\n📦 PRODUCTOS DISPONIBLES:")
        products = db.query(ProductModel).order_by(ProductModel.id_key).all()
        for prod in products:
            category = db.query(CategoryModel).get(prod.category_id)
            print(f"   #{prod.id_key}: {prod.name}")
            print(f"      💰 ${prod.price:,.2f} | 📦 {prod.stock} unidades")
            print(f"      🏷️  {category.name if category else 'Sin categoría'}")
            print(f"      🏷️  SKU: {prod.sku}")
        
        # Mostrar todas las direcciones detalladas
        print("\n📍 DIRECCIONES COMPLETAS:")
        addresses_list = db.query(
            AddressModel, 
            ClientModel.name, 
            ClientModel.lastname
        ).join(
            ClientModel, 
            AddressModel.client_id_key == ClientModel.id_key
        ).order_by(ClientModel.id_key).all()
        
        for addr, name, lastname in addresses_list:
            print(f"   👤 {name} {lastname}:")
            print(f"      🏠 {addr.street}")
            print(f"      🏙️  {addr.city}, {addr.state}")
            print(f"      📮 CP: {addr.zip_code}")
        
        print("\n✅ Base de datos actualizada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

def verify_client_order():
    """Función para verificar el orden actual de clientes"""
    print("\n🔍 Verificando orden actual de clientes...")
    db = SessionLocal()
    
    try:
        clients = db.query(ClientModel).order_by(ClientModel.id_key).all()
        
        print("   ID | Nombre      | Apellido    | Email")
        print("   " + "-" * 50)
        for client in clients:
            print(f"   {client.id_key:3} | {client.name:11} | {client.lastname:11} | {client.email}")
        
        return clients
    finally:
        db.close()

if __name__ == "__main__":
    # Primero mostrar el orden actual
    verify_client_order()
    
    # Preguntar si continuar
    respuesta = input("\n¿Continuar con la actualización? (s/n): ").lower()
    
    if respuesta == 's':
        update_database()
    else:
        print("Operación cancelada.")