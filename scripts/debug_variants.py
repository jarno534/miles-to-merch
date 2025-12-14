from app import create_app
from models import Variant, Product

app = create_app()

with app.app_context():
    products = Product.query.all()
    print(f"Found {len(products)} products.")
    for p in products:
        print(f"Product: {p.name} (ID: {p.id})")
        variants = p.variants.all()
        for v in variants:
            print(f"  - VarID: {v.id}, Color: {v.color}, Size: {v.size}, BasePath: '{v.image_base_path}', Image: '{v.image}'")
