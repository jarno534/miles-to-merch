import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
from app import create_app, db
from models import Product, Variant
from dotenv import load_dotenv

load_dotenv(override=True)
API_KEY = os.environ.get('PRINTFUL_API_KEY')
headers = {'Authorization': f'Bearer {API_KEY}'}

app = create_app()

def sync():
    with app.app_context():
        products = Product.query.all()
        print(f"Found {len(products)} products to sync.")
        
        for p in products:
            print(f"Syncing Product {p.id} (Printful ID {p.printful_product_id})...")
            try:
                res = requests.get(f'https://api.printful.com/products/{p.printful_product_id}', headers=headers)
                res.raise_for_status()
                data = res.json()
                prod_data = data.get('result', {}).get('product', {})
                
                # Update Name
                p.printful_name = prod_data.get('title')
                
                # Update Image (Force overwrite to ensure valid URL)
                p.product_image_url = prod_data.get('image')
                print(f"  -> Set Image: {p.product_image_url}")
                print(f"  -> Set Name: {p.printful_name}")
                
                # --- Step 1.5: Get Store ID (Required for templates) ---
                store_id = None
                try:
                    s_res = requests.get('https://api.printful.com/stores', headers=headers)
                    if s_res.status_code == 200:
                        stores = s_res.json().get('result', [])
                        if stores:
                            store_id = stores[0].get('id')
                            print(f"  -> Using Store ID: {store_id}")
                except Exception as e:
                    print(f"  -> Warning: Could not fetch store ID: {e}")

                # --- Step 2: Fetch Templates (Print Areas & Placements) ---
                print(f"  -> Fetching Templates for Product {p.printful_product_id}...")
                template_map = {}
                variant_tpl_map = {}
                
                try:
                    # Use query param for store_id
                    url = f'https://api.printful.com/mockup-generator/templates/{p.printful_product_id}'
                    if store_id:
                        url += f'?store_id={store_id}'
                        
                    tpl_res = requests.get(url, headers=headers)
                    if tpl_res.status_code == 200:
                        tpl_data = tpl_res.json().get('result', {})
                        
                        # Index templates by ID for fast lookup
                        # Index templates by ID for fast lookup
                        # map: template_id -> template_object (flat)
                        template_map = {}
                        for t in tpl_data.get('templates', []):
                            tid = t.get('template_id')
                            template_map[tid] = t

                        # Index variant mappings
                        # map: variant_id -> { placement_name -> template_id }
                        variant_tpl_map = {}
                        for vm in tpl_data.get('variant_mapping', []):
                            vid = vm.get('variant_id')
                            v_map = {}
                            for t_ref in vm.get('templates', []):
                                v_map[t_ref.get('placement')] = t_ref.get('template_id')
                            variant_tpl_map[vid] = v_map
                            
                        # Store this mapping for use in the loop below
                    else:
                        print(f"     [!] Failed to get templates: {tpl_res.status_code}")
                        template_map = {}
                        variant_tpl_map = {}
                except Exception as e:
                    print(f"     [!] Template Error: {e}")
                    template_map = {}
                    variant_tpl_map = {}

                # Sync Variants
                pf_variants = {v['id']: v for v in data.get('result', {}).get('variants', [])}
                
                # Check existing variants
                existing_ids = set()
                for v in p.variants:
                    existing_ids.add(v.printful_variant_id)
                    pf_v = pf_variants.get(v.printful_variant_id)
                    if pf_v:
                        v.printful_price = float(pf_v.get('price', 0))
                        v.in_stock = pf_v.get('in_stock', True)
                        v.image = pf_v.get('image') # Fix: Sync Variant Image
                        
                        # --- UPDATE PRINT AREAS ---
                        if v.printful_variant_id in variant_tpl_map:
                            my_areas = {}
                            v_mapping = variant_tpl_map[v.printful_variant_id]
                            for placement, tpl_id in v_mapping.items():
                                if tpl_id in template_map:
                                    t_data = template_map[tpl_id]
                                    
                                    # Data is flat on the template object
                                    if t_data.get("print_area_width"):
                                        my_areas[placement] = {
                                            "width": t_data.get("print_area_width"),
                                            "height": t_data.get("print_area_height"),
                                            "top": t_data.get("print_area_top"),
                                            "left": t_data.get("print_area_left"),
                                            "mockup_width": t_data.get("template_width"),
                                            "mockup_height": t_data.get("template_height"),
                                            "image_url": t_data.get("image_url") # Bonus: store specific image
                                        }
                            
                            if my_areas:
                                v.print_areas = my_areas
                                print(f"    -> Variant {v.id}: Updated {len(my_areas)} print areas.")
                                
                        print(f"    -> Updated Variant {v.id}: Price={v.printful_price}, Stock={v.in_stock}")
                        
                # Add MISSING variants
                for pf_id, pf_v in pf_variants.items():
                    if pf_id not in existing_ids:
                        print(f"    -> Adding NEW Variant {pf_id} ({pf_v.get('color')}, {pf_v.get('size')})")
                        
                        color_name = (pf_v.get('color') or '').lower()
                        merch_type = 'dark' if any(x in color_name for x in ['black', 'navy', 'dark', 'heather']) else 'light'
                        
                        # Resolve Print Areas for new variant
                        my_areas = {}
                        if pf_id in variant_tpl_map:
                            v_mapping = variant_tpl_map[pf_id]
                            for placement, tpl_id in v_mapping.items():
                                if tpl_id in template_map:
                                    t_data = template_map[tpl_id]
                                    if t_data.get("print_area_width"):
                                        my_areas[placement] = {
                                            "width": t_data.get("print_area_width"),
                                            "height": t_data.get("print_area_height"),
                                            "top": t_data.get("print_area_top"),
                                            "left": t_data.get("print_area_left"),
                                            "mockup_width": t_data.get("template_width"),
                                            "mockup_height": t_data.get("template_height"),
                                            "image_url": t_data.get("image_url")
                                        }

                        new_var = Variant(
                            product_id=p.id,
                            printful_variant_id=pf_id,
                            color=pf_v.get('color') or 'Unknown',
                            color_code=pf_v.get('color_code'),
                            size=pf_v.get('size') or 'One Size',
                            price=25.0, # Default Retail Price
                            printful_price=float(pf_v.get('price', 0)),
                            in_stock=pf_v.get('in_stock', True),
                            merch_color_type=merch_type,
                            image=pf_v.get('image'),
                            image_urls={'mockup': pf_v.get('image')},
                            available_regions=["EU", "US"],
                            is_active=False,
                            print_areas=my_areas  # <--- SAVE HERE
                        )
                        if my_areas:
                            print(f"       With {len(my_areas)} print areas.")
                        db.session.add(new_var)

            except Exception as e:
                print(f"  -> Failed: {e}")
        
        db.session.commit()
        print("Sync complete!")

if __name__ == "__main__":
    sync()
