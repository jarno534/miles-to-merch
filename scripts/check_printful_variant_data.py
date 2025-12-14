import requests
import os
from dotenv import load_dotenv
import json

load_dotenv(override=True)
API_KEY = os.environ.get('PRINTFUL_API_KEY')

def check():
    # ID 71 is T-Shirt
    res = requests.get('https://api.printful.com/products/71', headers={'Authorization': f'Bearer {API_KEY}'})
    data = res.json().get('result', {})
    variants = data.get('variants', [])
    
    if variants:
        v = variants[0]
        print("Variant Keys:", v.keys())
        print("Example Variant:", json.dumps(v, indent=2))
    else:
        print("No variants found")

if __name__ == "__main__":
    check()
