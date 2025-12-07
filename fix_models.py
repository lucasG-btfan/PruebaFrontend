"""
Script para estandarizar nombres de modelos.
"""
import os
import sys

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_and_fix_imports():  
    """Verificar y corregir importaciones."""
    
    print("🔍 Verificando importaciones...")
    
    # Archivos que necesitan revisión
    files_to_check = [
        'models/client.py',
        'services/client_service.py',
        'repositories/client_repository.py',
        'controllers/client_controller.py'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"\n📄 Revisando: {file_path}")
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Verificar si usa Client o ClientModel
            if 'ClientModel' in content:
                print(f"  ✓ Ya usa ClientModel")
            elif 'from models.client import Client' in content:
                print(f"  ⚠ Usa 'Client', debería usar 'ClientModel'")
            else:
                print(f"  ? No se encontraron referencias claras a Client")
    
    print("\n" + "="*50)
    print("🎯 RECOMENDACIÓN:")
    print("1. En models/__init__.py ya tienes Client importado como ClientModel")
    print("2. El problema está en controllers/client_controller.py")
    print("\n📋 SOLUCIÓN TEMPORAL:")
    print("Usa este servidor simplificado primero:")

if __name__ == "__main__":
    check_and_fix_imports() 