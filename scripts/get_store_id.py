
import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('PRINTFUL_API_KEY')
if not token:
    print("No API Key found")
    exit(1)

print(f"Token Prefix: {token[:5]}...")

try:
    res = requests.get('https://api.printful.com/stores', headers={'Authorization': f'Bearer {token}'})
    print(f"Status: {res.status_code}")
    print(res.text)
except Exception as e:
    print(f"Error: {e}")
