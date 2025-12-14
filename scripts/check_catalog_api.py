import requests
import json
import os
from dotenv import load_dotenv

BASE_URL = "http://localhost:5000"
EMAIL = "jarno.blomme@telenet.be"
PASSWORD = "admin" 

def check():
    s = requests.Session()
    # Login
    res = s.post(f"{BASE_URL}/auth/login", json={'email': EMAIL, 'password': PASSWORD})
    print(f"Login Status: {res.status_code}")
    
    # Fetch Catalog
    try:
        res = s.get(f"{BASE_URL}/api/printful/catalog")
        print(f"Catalog Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print(f"Items count: {len(data)}")
            if len(data) > 0:
                print(f"first item: {data[0]}")
        else:
            print(f"Error: {res.text}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    check()
