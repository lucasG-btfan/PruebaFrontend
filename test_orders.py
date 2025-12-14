import requests
import json

BASE_URL = "http://localhost:8000"  # Cambia a tu URL de Render si es necesario

def test_endpoints():
    print("1. Probando GET /orders")
    try:
        response = requests.get(f"{BASE_URL}/orders")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total órdenes: {data.get('total', 0)}")
            if data.get('orders'):
                print(f"Primera orden ID: {data['orders'][0].get('id_key')}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n2. Creando una orden de prueba")
    try:
        # Primero necesitas un cliente existente
        order_data = {
            "client_id": 1,  # Cambia por un ID de cliente que exista
            "total": 99.99,
            "delivery_method": 1,
            "status": 1,
            "bill_id": None,  # Opcional
            "order_details": [
                {
                    "product_id": 1,  # Cambia por un producto existente
                    "quantity": 2,
                    "price": 49.99
                }
            ]
        }
        
        response = requests.post(f"{BASE_URL}/orders", json=order_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            order = response.json()
            order_id = order.get('order_id')
            print(f"Orden creada con ID: {order_id}")
            
            print("\n3. Probando GET /orders/{id}")
            response = requests.get(f"{BASE_URL}/orders/{order_id}")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Orden encontrada: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_endpoints()