"""
One-time script to add Phase 3 columns to the production PostgreSQL database.
Run this via the Render Shell: python scripts/add_phase3_columns_prod.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from sqlalchemy import text, inspect

app = create_app()

with app.app_context():
    engine = db.engine
    inspector = inspect(engine)

    # Check and add print_areas to variant
    variant_cols = [col['name'] for col in inspector.get_columns('variant')]
    if 'print_areas' not in variant_cols:
        print("Adding print_areas to variant...")
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE variant ADD COLUMN print_areas JSON"))
            conn.commit()
        print("  Done.")
    else:
        print("variant.print_areas already exists, skipping.")

    # Check and add sponsored_settings to product
    product_cols = [col['name'] for col in inspector.get_columns('product')]
    if 'sponsored_settings' not in product_cols:
        print("Adding sponsored_settings to product...")
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE product ADD COLUMN sponsored_settings JSON"))
            conn.commit()
        print("  Done.")
    else:
        print("product.sponsored_settings already exists, skipping.")

    print("\nMigration complete! All Phase 3 columns are now in place.")
