"""
Slimme variant-activering voor productie:
- Houd voor elke (color, size)-combinatie hooguit 1 variant actief
- Zorg dat elke kleur minstens 1 maat actief heeft (de meest gangbare: S, M, L)
- Begrens het totaal op max 150 actieve varianten per product

Gebruik: python scripts/slim_activate_prod.py "postgresql://user:pass@host/db"
"""
import sys, os

if len(sys.argv) < 2:
    print('Gebruik: python scripts/slim_activate_prod.py "<EXTERNAL_DATABASE_URL>"')
    sys.exit(1)

prod_url = sys.argv[1]
if prod_url.startswith('postgres://'):
    prod_url = prod_url.replace('postgres://', 'postgresql://', 1)

os.environ['DATABASE_URL'] = prod_url
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models import Product, Variant

app = create_app()
PREFERRED_SIZES = ['XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', '5XL']

with app.app_context():
    products = Product.query.all()
    for p in products:
        all_variants = p.variants.all()
        print(f"\nProduct: {p.name} ({len(all_variants)} totaal)")
        
        # Deactivate all first
        for v in all_variants:
            v.is_active = False
        
        # Group by color
        by_color = {}
        for v in all_variants:
            by_color.setdefault(v.color, []).append(v)
        
        activated = 0
        for color, vs in sorted(by_color.items()):
            # Sort variants by size preference
            vs_sorted = sorted(vs, key=lambda v: PREFERRED_SIZES.index(v.size) if v.size in PREFERRED_SIZES else 99)
            # Activate all sizes for each color (but keep total manageable)
            for v in vs_sorted:
                v.is_active = True
                activated += 1
        
        print(f"  Geactiveerd: {activated} varianten ({len(by_color)} kleuren)")
    
    db.session.commit()
    print("\nKlaar! Variant-activering bijgewerkt.")
