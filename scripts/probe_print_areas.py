
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
PRINTFUL_API_KEY = os.getenv('PRINTFUL_API_KEY')
HEADERS = {'Authorization': f'Bearer {PRINTFUL_API_KEY}'}

def probe_product(product_id):
    url = f"https://api.printful.com/products/{product_id}"
    print(f"Fetching {url}...")
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        print(f"Error: {r.status_code} {r.text}")
        return

    data = r.json().get('result', {})
    
    print(f"\n--- Product: {data.get('product', {}).get('title')} ---")
    
    # Inspect Variants for dimensions
    variants = data.get('variants', [])
    if variants:
        v = variants[0]
        print(f"Sample Variant ID: {v.get('id')}")
        print(f"Keys in variant: {list(v.keys())}")
        # Check for print area info in variant?
    
    # Printful 'products/{id}' acts as catalog info.
    # Where are print areas?
    # Usually in 'files' or 'dimensions'?
    # Or in 'printfiles'?
    
    
    # Check 'files' in product
    # Files print removed

    
    # Fetch Store ID (Required for templates)
    print("Fetching Store ID...")
    store_id = 16718510
    print(f"Using Hardcoded Store ID: {store_id}")


    # Check Mockup Templates Endpoint (Often has print area sizes)
    print("\n--- Checking /mockup-generator/templates/{id} ---")
    
    # Try query param instead of header
    url = f"https://api.printful.com/mockup-generator/templates/{product_id}?store_id={store_id}"
    print(f"Requesting: {url}")
    r2 = requests.get(url, headers=HEADERS)
    print(f"Status: {r2.status_code}")
    if r2.status_code == 200:
        tpl_data = r2.json().get('result', {})
        print(f"Template Keys: {list(tpl_data.keys())}")
        # Inspect 'variant_mapping' or 'placements'
        placements = tpl_data.get('placements', {})
        print(f"Placements Keys: {list(placements.keys())}")
        
        # Check one placement details
        if placements:
             first_key = list(placements.keys())[0]
             print(f"Placement '{first_key}' details: {json.dumps(placements[first_key], indent=2)}")
             
        # Check variant_mapping to see if sizes map to specific templates
        print(f"Variant Mapping count: {len(tpl_data.get('variant_mapping', []))}")
        
        output_path = r'd:\Miles to Merch\probe_output.json'
        with open(output_path, 'w') as f:
            json.dump(tpl_data, f, indent=2)
            print(f"Dumped full template data to {output_path}")
    else:
        print(f"Error fetching templates: {r2.text}")
             
if __name__ == '__main__':
    probe_product(71)
