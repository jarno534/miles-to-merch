import os
import requests
import json
from dotenv import load_dotenv

load_dotenv(override=True)
API_KEY = os.environ.get('PRINTFUL_API_KEY')
headers = {'Authorization': f'Bearer {API_KEY}'}

store_id = 16718510

url = f'https://api.printful.com/mockup-generator/templates/71?store_id={store_id}'
res = requests.get(url, headers=headers)
data = res.json()

print(json.dumps(data.get('result', {}).get('mockups', []) , indent=2)[:2000])

