# test_relationships.py
from config.database_render import SessionLocal
from models.bill import BillModel
from models.order import OrderModel

def test_relationships():
    db = SessionLocal()
    try:
        print("🔍 Verificando relaciones Bill-Order...")
        bill_rels = BillModel.__mapper__.relationships.keys()
        order_rels = OrderModel.__mapper__.relationships.keys()
        
        print(f"Relaciones en BillModel: {list(bill_rels)}")
        print(f"Relaciones en OrderModel: {list(order_rels)}")
        
        # Verificar foreign keys
        for col in BillModel.__table__.columns:
            if col.foreign_keys:
                print(f"Bill FK: {col.name} -> {list(col.foreign_keys)[0].column}")
                
        for col in OrderModel.__table__.columns:
            if col.foreign_keys:
                print(f"Order FK: {col.name} -> {list(col.foreign_keys)[0].column}")
        
        print("✅ Verificación completada")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    test_relationships()