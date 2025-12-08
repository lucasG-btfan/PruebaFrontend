# monitor_render.py
import requests
import time
import sys

def monitor_deploy(service_url, check_interval=30, max_checks=20):
    """
    Monitor deployment on Render.
    """
    print(f"👀 Monitoring deployment of {service_url}")
    print(f"⏱️  Checking every {check_interval} seconds...")
    
    for check_num in range(1, max_checks + 1):
        print(f"\n📊 Check #{check_num} at {time.strftime('%H:%M:%S')}")
        
        try:
            # Try health endpoint
            response = requests.get(f"{service_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SERVICE IS LIVE!")
                print(f"   Status: {data.get('status', 'N/A')}")
                print(f"   Database: {data.get('database', 'N/A')}")
                print(f"   Environment: {data.get('environment', 'N/A')}")
                
                # Test additional endpoints
                print("\n🔍 Testing additional endpoints:")
                endpoints = ["/", "/docs", "/api/v1/products"]
                for endpoint in endpoints:
                    try:
                        endpoint_response = requests.get(
                            f"{service_url}{endpoint}", 
                            timeout=5
                        )
                        print(f"   {endpoint}: Status {endpoint_response.status_code}")
                    except:
                        print(f"   {endpoint}: Failed")
                
                print("\n🎉 DEPLOYMENT SUCCESSFUL!")
                return True
                
            else:
                print(f"⚠️ Service returned status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection refused (service starting or not deployed)")
        except requests.exceptions.Timeout:
            print("⏰ Request timeout (service might be starting)")
        except Exception as e:
            print(f"⚠️ Error: {e}")
        
        if check_num < max_checks:
            print(f"⏳ Waiting {check_interval} seconds before next check...")
            time.sleep(check_interval)
    
    print(f"\n❌ Service did not become available after {max_checks} checks")
    return False

if __name__ == "__main__":
    # Cambia esta URL por la de tu servicio en Render
    SERVICE_URL = "https://ecommerce-backend.onrender.com"  # O la nueva si creas v2
    
    if len(sys.argv) > 1:
        SERVICE_URL = sys.argv[1]
    
    success = monitor_deploy(SERVICE_URL)
    sys.exit(0 if success else 1)