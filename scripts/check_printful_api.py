import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)
API_KEY = os.environ.get('PRINTFUL_API_KEY')

if not API_KEY:
    print("No API Key found")
    exit()

headers = {'Authorization': f'Bearer {API_KEY}'}
url = 'https://api.printful.com/products/19'

print(f"Fetching {url}...")
try:
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    data = res.json()
    print("Response Keys:", data.get('result', {}).keys())
    # Check for 'url' or 'slug'
    product = data.get('result', {}).get('product', {})
    print("Product Details:", product)
except Exception as e:
    print(f"Error: {e}")
