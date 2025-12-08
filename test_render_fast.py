# test_render_fast.py
"""
Test rápido para verificar si el backend en Render está funcionando.
"""
import requests
import json

def test_endpoints():
    base_url = "https://ecommerce-backend.onrender.com"
    
    endpoints = [
        ("/", "Root", {}),
        ("/health", "Health", {}),
        ("/api/v1/products", "Products", {"skip": 0, "limit": 10}),
    ]
    
    print("🔍 Testing Render Backend...")
    print(f"URL: {base_url}")
    print("-" * 60)
    
    for endpoint, name, params in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, params=params, timeout=10)
            
            print(f"{name}:")
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"  ✅ Success: {json.dumps(data)[:100]}...")
                except:
                    print(f"  ✅ Success (non-JSON): {response.text[:100]}...")
            elif response.status_code == 404:
                print(f"  ❌ Not Found (ruta incorrecta)")
            elif response.status_code == 500:
                print(f"  ❌ Server Error")
            else:
                print(f"  ⚠️ Unexpected: {response.status_code}")
                
            # Check CORS headers
            if 'Access-Control-Allow-Origin' in response.headers:
                print(f"  🌍 CORS Header: {response.headers['Access-Control-Allow-Origin']}")
            else:
                print(f"  ⚠️ No CORS header found")
                
        except requests.exceptions.ConnectionError:
            print(f"{name}: ❌ Connection refused")
        except requests.exceptions.Timeout:
            print(f"{name}: ⏰ Timeout")
        except Exception as e:
            print(f"{name}: ❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    test_endpoints()