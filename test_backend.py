import requests
import hashlib
import base64
import os

def test_login():
    print("🔐 Probando login...")
    
    url = "https://comercio-digital.onrender.com/api/v1/auth/login"
    data = {
        "email": "admin@example.com",
        "password": "coleMC_89"  # ¡PON TU CONTRASEÑA REAL AQUÍ!
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            token = response.json().get('access_token')
            if token:
                print(f"✅ Token recibido ({len(token)} caracteres)")
                print(f"Token muestra: {token[:50]}...")
                
                # Decodificar para ver contenido
                parts = token.split('.')
                if len(parts) == 3:
                    import json
                    payload = json.loads(base64.b64decode(parts[1] + '==='))
                    print(f"📋 Payload: {payload}")
            else:
                print("❌ No se recibió token en la respuesta")
        
        return response.status_code, response.json() if response.status_code == 200 else None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def generate_password_hash():
    """Genera hash para la contraseña si necesitas actualizarla"""
    password = "123456"  # O tu contraseña real
    salt = base64.b64encode(os.urandom(32)).decode('utf-8')
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    
    print(f"\n🔧 Para actualizar contraseña en BD:")
    print(f"Salt: {salt}")
    print(f"Hash: {password_hash}")
    
    # Comando SQL para actualizar
    print(f"\n📝 Comando SQL:")
    print(f"UPDATE clients SET password_hash = '{password_hash}', password_salt = '{salt}' WHERE id_key = 0;")

if __name__ == "__main__":
    print("🚀 Testeando backend...")
    print("-" * 50)
    
    status, data = test_login()
    
    if status != 200:
        print("\n🔧 Generando hash para contraseña '123456':")
        generate_password_hash()