
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('PRINTFUL_API_KEY')
print(f"Token: {token[:5]}...")

# Product 71 (T-Shirt)
url = "https://api.printful.com/products/71"
print(f"Fetching {url}...")
res = requests.get(url, headers={'Authorization': f'Bearer {token}'})

if res.status_code == 200:
    data = res.json().get('result', {}).get('product', {})
    files = data.get('files', [])
    print(f"Found {len(files)} files/placements.")
    
    for f in files:
        if f.get('type') == 'front':
            print("--- Front Placement ---")
            print(json.dumps(f, indent=2))
        elif f.get('type') == 'back':
            print("--- Back Placement ---")
            print(json.dumps(f, indent=2))
            
else:
    print(f"Error: {res.status_code} {res.text}")
