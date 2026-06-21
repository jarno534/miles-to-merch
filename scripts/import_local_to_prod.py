"""
Importeert producten vanuit de lokale database naar de productiedatabase op Render.
Dit script:
1. Leest alle producten + actieve varianten uit de lokale SQLite
2. Schrijft ze naar de productie-PostgreSQL

Gebruik:
  python scripts/import_local_to_prod.py "postgresql://user:pass@host/db"
"""
import sys
import os

if len(sys.argv) < 2:
    print('Gebruik: python scripts/import_local_to_prod.py "<EXTERNAL_DATABASE_URL>"')
    sys.exit(1)

prod_url = sys.argv[1]
if prod_url.startswith('postgres://'):
    prod_url = prod_url.replace('postgres://', 'postgresql://', 1)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Stap 1: Lees lokale data ---
print("Stap 1: Lokale database uitlezen...")
from app import create_app
from models import Product, Variant

local_app = create_app()
local_data = []

with local_app.app_context():
    products = Product.query.all()
    print(f"  Gevonden: {len(products)} producten lokaal")
    for p in products:
        variants = p.variants.filter_by(is_active=True).all()
        print(f"  - Product {p.id}: '{p.name}' | {len(variants)} actieve varianten")
        local_data.append({
            'name': p.name,
            'description': p.description,
            'printful_product_id': p.printful_product_id,
            'printful_name': p.printful_name,
            'product_image_url': p.product_image_url,
            'sponsored_settings': getattr(p, 'sponsored_settings', {}) or {},
            'variants': [{
                'printful_variant_id': v.printful_variant_id,
                'color': v.color,
                'color_code': v.color_code,
                'size': v.size,
                'price': v.price,
                'printful_price': v.printful_price,
                'in_stock': v.in_stock,
                'merch_color_type': v.merch_color_type,
                'image': v.image,
                'image_urls': v.image_urls,
                'image_base_path': v.image_base_path,
                'available_regions': v.available_regions,
                'is_active': v.is_active,
                'print_areas': getattr(v, 'print_areas', {}) or {},
            } for v in p.variants.all()]  # All variants, not just active
        })

print(f"\nStap 2: Verbinden met productiedatabase...")
print(f"  URL: {prod_url[:70]}...")

# --- Stap 2: Schrijf naar productiedatabase ---
os.environ['DATABASE_URL'] = prod_url

# Maak een nieuwe app-instantie met de prod-URL
import importlib
import app as app_module
importlib.invalidate_caches()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from extensions import db as ext_db

# Directe verbinding met prod DB
engine = create_engine(prod_url)
Session = scoped_session(sessionmaker(bind=engine))
prod_session = Session()

# Importeer models zodat we ze kunnen gebruiken
from models import Product as ProdProduct, Variant as ProdVariant

print(f"\nStap 3: Producten importeren naar productiedatabase...")
imported = 0
skipped = 0

for p_data in local_data:
    # Controleer of product al bestaat
    existing = prod_session.query(ProdProduct).filter_by(
        printful_product_id=p_data['printful_product_id']
    ).first()
    
    if existing:
        print(f"  Product '{p_data['name']}' bestaat al, overgeslagen.")
        skipped += 1
        continue
    
    # Maak nieuw product aan
    new_product = ProdProduct(
        name=p_data['name'],
        description=p_data['description'],
        printful_product_id=p_data['printful_product_id'],
        printful_name=p_data['printful_name'],
        product_image_url=p_data['product_image_url'],
        sponsored_settings=p_data['sponsored_settings'],
    )
    prod_session.add(new_product)
    prod_session.flush()  # Krijg het ID
    
    # Voeg varianten toe
    variant_count = 0
    for v_data in p_data['variants']:
        new_variant = ProdVariant(
            product_id=new_product.id,
            printful_variant_id=v_data['printful_variant_id'],
            color=v_data['color'],
            color_code=v_data['color_code'],
            size=v_data['size'],
            price=v_data['price'],
            printful_price=v_data['printful_price'],
            in_stock=v_data['in_stock'],
            merch_color_type=v_data['merch_color_type'],
            image=v_data['image'],
            image_urls=v_data['image_urls'],
            image_base_path=v_data['image_base_path'],
            available_regions=v_data['available_regions'],
            is_active=v_data['is_active'],
            print_areas=v_data['print_areas'],
        )
        prod_session.add(new_variant)
        variant_count += 1
    
    print(f"  OK Product '{p_data['name']}' geimporteerd met {variant_count} varianten")
    imported += 1

prod_session.commit()
prod_session.close()

print(f"\n=== Import voltooid ===")
print(f"  Geïmporteerd: {imported} producten")
print(f"  Overgeslagen: {skipped} producten (al aanwezig)")
print(f"\nDe website zou nu producten moeten tonen!")
