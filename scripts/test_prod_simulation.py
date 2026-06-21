"""
Test what happens when products route runs with the current code.
Simulates the production environment.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import traceback

try:
    from app import create_app
    from models import Product
    
    app = create_app()
    
    with app.app_context():
        print("App context OK")
        try:
            products = Product.query.all()
            print(f"Products query OK: {len(products)} products")
            for p in products:
                try:
                    d = p.to_dict()
                    print(f"  Product {p.id} to_dict OK: {p.name}")
                except Exception as e2:
                    print(f"  Product {p.id} to_dict FAILED: {e2}")
                    traceback.print_exc()
        except Exception as e:
            print(f"Products query FAILED: {e}")
            traceback.print_exc()
            
except Exception as e:
    print(f"App creation FAILED: {e}")
    traceback.print_exc()
