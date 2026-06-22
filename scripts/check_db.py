import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import Product, Variant

app = create_app()
with app.app_context():
    products = Product.query.all()
    print(f'Total products: {len(products)}')
    for p in products:
        active = p.variants.filter_by(is_active=True).count()
        total = p.variants.count()
        print(f'  Product {p.id}: "{p.name}" | Total: {total} | Active: {active}')
    
    print(f'\nTotal active variants in DB: {Variant.query.filter_by(is_active=True).count()}')
    print(f'Total variants in DB: {Variant.query.count()}')
