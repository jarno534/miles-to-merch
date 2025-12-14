import requests
import os
from dotenv import load_dotenv

load_dotenv(override=True)
API_KEY = os.environ.get('PRINTFUL_API_KEY')

def check():
    res = requests.get('https://api.printful.com/products', headers={'Authorization': f'Bearer {API_KEY}'})
    data = res.json().get('result', [])
    if data:
        print("Keys:", data[0].keys())
        print("Example:", data[0])

if __name__ == "__main__":
    check()
