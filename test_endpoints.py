# test_endpoints.py
import requests

BACKEND_URL = "https://ecommerce-backend.onrender.com"

endpoints = [
    "/",
    "/health",
    "/docs",
    "/api/v1/products",
    "/api/v1/orders",
]

print(f"Testing backend at: {BACKEND_URL}")
print("=" * 60)

for endpoint in endpoints:
    try:
        url = f"{BACKEND_URL}{endpoint}"
        print(f"Testing: {endpoint}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ {endpoint}: {response.status_code}")
            if endpoint == "/health":
                print(f"   Response: {response.json()}")
        else:
            print(f"❌ {endpoint}: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
    except Exception as e:
        print(f"❌ {endpoint}: ERROR - {str(e)}")
    
    print("-" * 40)