# check_render_status.py
import requests
import time

def check_render_service():
    url = "https://ecommerce-backend.onrender.com"
    
    print("🔍 Checking Render service status...")
    
    # 1. Check root endpoint
    try:
        response = requests.get(url, timeout=10)
        print(f"✅ Root endpoint: Status {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.text[:100]}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
    
    # 2. Check health endpoint
    try:
        response = requests.get(f"{url}/health", timeout=10)
        print(f"✅ /health: Status {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ /health failed: {e}")
    
    # 3. Check if it's a Render default page
    try:
        response = requests.get(url, timeout=10)
        if "Render" in response.text and "deploy" in response.text.lower():
            print("⚠️ This appears to be Render's default landing page")
            print("   The service might not be deployed correctly")
    except:
        pass

if __name__ == "__main__":
    check_render_service()