from app import app
from models import Product
import traceback

print("Starting debug script...")
try:
    with app.app_context():
        print("Querying all products...")
        products = Product.query.all()
        print(f"Found {len(products)} products.")
        
        for p in products:
            print(f"Processing product: {p.name}")
            try:
                data = p.to_dict()
                print("Serialize success!")
                print(data)
            except Exception as e:
                print(f"Error serializing product {p.id}: {e}")
                traceback.print_exc()
except Exception as e:
    print(f"Global error: {e}")
    traceback.print_exc()
