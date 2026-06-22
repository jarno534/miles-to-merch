from app import create_app
from models import Variant

app = create_app()

with app.app_context():
    variants = Variant.query.limit(20).all()
    print(f"Checking {len(variants)} variants...")
    for v in variants:
        print(f"ID: {v.id} | Color: {v.color} | Image: {v.image}")
