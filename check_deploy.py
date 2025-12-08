# check_deploy.py
import requests
import time

def check_service(url, max_attempts=30, delay=5):
    """
    Check if service is responding.
    """
    print(f"🔍 Checking service at {url}")
    
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"Attempt {attempt}/{max_attempts}...")
            response = requests.get(f"{url}/health", timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Service is UP! Response: {response.json()}")
                return True
            else:
                print(f"⚠️ Service returned status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection refused (service may be starting up)")
        except requests.exceptions.Timeout:
            print(f"⏰ Request timeout")
        except Exception as e:
            print(f"⚠️ Error: {e}")
        
        if attempt < max_attempts:
            print(f"Waiting {delay} seconds before next attempt...")
            time.sleep(delay)
    
    print("❌ Service did not become available in time")
    return False

if __name__ == "__main__":
    # URL de tu backend en Render
    service_url = "https://ecommerce-backend.onrender.com"  # Cambia esto por tu URL real
    
    if check_service(service_url):
        # Test additional endpoints
        endpoints = ["/", "/docs", "/api/v1/products"]
        for endpoint in endpoints:
            try:
                response = requests.get(f"{service_url}{endpoint}", timeout=10)
                print(f"✅ {endpoint}: Status {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint}: Failed - {e}")
    else:
        print("❌ Service check failed")