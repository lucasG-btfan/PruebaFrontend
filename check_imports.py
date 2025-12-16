"""
Script para diagnosticar problemas de importación circular
Ejecuta esto localmente antes de hacer deploy a Render
"""
from __future__ import annotations
import sys
import traceback

print("=" * 60)
print("DIAGNÓSTICO DE IMPORTACIONES")
print("=" * 60)

# Test 1: Importar order_schema
try:
    print("\n1. Importando order_schema...")
    from schemas import order_schema
    print("   ✓ order_schema importado correctamente")
    print(f"   - Clases disponibles: {[c for c in dir(order_schema) if not c.startswith('_')]}")
except Exception as e:
    print(f"   ✗ ERROR en order_schema:")
    print(f"   {e}")
    traceback.print_exc()

# Test 2: Importar order_detail_schema
try:
    print("\n2. Importando order_detail_schema...")
    from schemas import order_detail_schema
    print("   ✓ order_detail_schema importado correctamente")
    print(f"   - Clases disponibles: {[c for c in dir(order_detail_schema) if not c.startswith('_')]}")
except Exception as e:
    print(f"   ✗ ERROR en order_detail_schema:")
    print(f"   {e}")
    traceback.print_exc()

# Test 3: Importar bill_schema
try:
    print("\n3. Importando bill_schema...")
    from schemas import bill_schema
    print("   ✓ bill_schema importado correctamente")
    print(f"   - Clases disponibles: {[c for c in dir(bill_schema) if not c.startswith('_')]}")
except Exception as e:
    print(f"   ✗ ERROR en bill_schema:")
    print(f"   {e}")
    traceback.print_exc()

# Test 4: Importar desde __init__
try:
    print("\n4. Importando desde schemas.__init__...")
    from schemas import OrderSchema, OrderCreateSchema
    print("   ✓ Schemas importados desde __init__ correctamente")
    print(f"   - OrderSchema: {OrderSchema}")
    print(f"   - OrderCreateSchema: {OrderCreateSchema}")
except Exception as e:
    print(f"   ✗ ERROR en schemas.__init__:")
    print(f"   {e}")
    traceback.print_exc()

# Test 5: Crear instancia de OrderSchema
try:
    print("\n5. Creando instancia de OrderSchema...")
    from schemas import OrderSchema
    test_order = OrderSchema(
        id_key=1,
        client_id=1,
        total=100.0,
        delivery_method=1,
        status=1
    )
    print(f"   ✓ Instancia creada: {test_order}")
except Exception as e:
    print(f"   ✗ ERROR creando instancia:")
    print(f"   {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("DIAGNÓSTICO COMPLETADO")
print("=" * 60)