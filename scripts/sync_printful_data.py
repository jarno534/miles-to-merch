import os
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
                        print(f"    -> Updated Variant {v.id}: Price={v.printful_price}, Stock={v.in_stock}")
                        
                # Add MISSING variants
                for pf_id, pf_v in pf_variants.items():
                    if pf_id not in existing_ids:
                        print(f"    -> Adding NEW Variant {pf_id} ({pf_v.get('color')}, {pf_v.get('size')})")
                        
                        color_name = (pf_v.get('color') or '').lower()
                        merch_type = 'dark' if any(x in color_name for x in ['black', 'navy', 'dark', 'heather']) else 'light'
                        
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
                            is_active=False
                        )
                        db.session.add(new_var)

            except Exception as e:
                print(f"  -> Failed: {e}")
        
        db.session.commit()
        print("Sync complete!")

if __name__ == "__main__":
    sync()
