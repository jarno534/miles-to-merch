from app import create_app
from models import Product

app = create_app()

with app.app_context():
    products = Product.query.all()
    for p in products:
        print(f"Product: {p.name}, ID: {p.id}")
        print(f"  Printful Name: {p.printful_name}")
        print(f"  Image URL: {p.product_image_url}")
