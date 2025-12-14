import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)
API_KEY = os.environ.get('PRINTFUL_API_KEY')
headers = {'Authorization': f'Bearer {API_KEY}'}
url = 'https://api.printful.com/products/19' # Mug
url2 = 'https://api.printful.com/products/71' # Bella Canvas probably

def check(id):
    print(f"--- Checking ID {id} ---")
    try:
        res = requests.get(f'https://api.printful.com/products/{id}', headers=headers)
        data = res.json()
        prod = data.get('result', {}).get('product', {})
        print(f"Title: {prod.get('title')}")
        print(f"Type: {prod.get('type')}")
        print(f"Brand: {prod.get('brand')}")
        print(f"Model: {prod.get('model')}")
        print(f"Image: {prod.get('image')}")
    except Exception as e:
        print(e)

check(71)
