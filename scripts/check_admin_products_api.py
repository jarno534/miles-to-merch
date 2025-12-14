import requests
import json

BASE_URL = "http://localhost:5000"
EMAIL = "jarno.blomme@telenet.be"
PASSWORD = "admin" 

def check():
    s = requests.Session()
    # Login
    try:
        res = s.post(f"{BASE_URL}/auth/login", json={'email': EMAIL, 'password': PASSWORD})
        if res.status_code != 200:
            # Maybe already logged in? Or wrong password?
            # Try 'test'
            res = s.post(f"{BASE_URL}/auth/login", json={'email': EMAIL, 'password': 'test'})
            
        if res.status_code != 200:
            print("Login failed")
            return

        # Fetch Admin Products
        res = s.get(f"{BASE_URL}/api/admin/products")
        data = res.json()
        
        # Print first product
        if len(data) > 0:
            p = data[0]
            print(f"Product 0 Name: {p.get('name')}")
            print(f"Product 0 Image: {p.get('product_image_url')}")
            
            # Check Image Status
            img_url = p.get('product_image_url')
            if img_url:
                try:
                    img_res = requests.head(img_url)
                    print(f"Image Status Code: {img_res.status_code}")
                except Exception as e:
                    print(f"Image Check Failed: {e}")
        else:
            print("No products returned")
            
    except Exception as e:
        print(e)
            
if __name__ == "__main__":
    check()
