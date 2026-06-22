import requests
import os
import json
from dotenv import load_dotenv

load_dotenv(override=True)
API_KEY = os.environ.get('PRINTFUL_API_KEY')
headers = {'Authorization': f'Bearer {API_KEY}'}
STORE_ID = 16718510
PRODUCT_ID = 71

def probe():
    url = f'https://api.printful.com/mockup-generator/templates/{PRODUCT_ID}?store_id={STORE_ID}'
    print(f"Fetching: {url}")
    res = requests.get(url, headers=headers)
    
    if res.status_code != 200:
        print(f"Error {res.status_code}: {res.text}")
        return

    data = res.json().get('result', {})
    
    # 1. Check Placement Mapping
    print("\n--- Variant Mappings ---")
    vars_mapping = data.get('variant_mapping', [])
    if not vars_mapping:
         print("NO VARIANT MAPPING FOUND!")
    else:
        # Show first item
        v1 = vars_mapping[0]
        print(f"Variant {v1.get('variant_id')} maps to:")
        for t in v1.get('templates', []):
            print(f"  - Placement: {t.get('placement')} -> Template ID: {t.get('template_id')}")

    # 2. Check Templates
    print("\n--- Templates ---")
    templates = data.get('templates', [])
    print(f"Found {len(templates)} templates.")
    for t in templates[:3]:
        print(f"ID {t.get('template_id')}: Width={t.get('print_area_width')}, Image={t.get('image_url')}")

if __name__ == "__main__":
    probe()
