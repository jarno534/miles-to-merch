from flask import Flask, jsonify
from dotenv import load_dotenv
from config import Config
from models import User, Product, Variant, Design, Order # Variant is nieuw
from routes.auth import auth_bp
from routes.api import api_bp
from flask_migrate import Migrate
import os
import click
import requests
import json
from extensions import db, cors
from admin import setup_admin

load_dotenv()
migrate = Migrate()

# --- De App Factory Functie ---
def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    allowed_origins = [
        "https://miles-to-merch.vercel.app",
        "http://localhost:8081"
    ]
    cors.init_app(
        app,
        origins=allowed_origins,
        supports_credentials=True
    )

    setup_admin(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    @app.route('/')
    def index():
        return jsonify({'message': 'Welcome!'})

    return app

# --- Maak een app instance aan speciaal voor de CLI commando's ---
app = create_app()

# --- Helper Functies voor CLI ---
def get_color_type_from_name(color_name):
    """Bepaalt 'light' of 'dark' op basis van de kleurnaam."""
    dark_keywords = ['black', 'charcoal', 'navy', 'dark', 'forest', 'maroon', 'burgundy']
    if color_name is None: return 'light'
    for keyword in dark_keywords:
        if keyword in color_name.lower():
            return 'dark'
    return 'light'

# --- CLI Commando's ---
@app.cli.command("seed-db")
def seed_db_command():
    """Vult de database met één testproduct en variant."""
    db.drop_all()
    db.create_all()
    print("Database is gereset.")

    if Variant.query.first() is not None:
        print("Database bevat al varianten. Seeden wordt overgeslagen.")
        return

    print("Database vullen met een testproduct...")
    
    product1 = Product(
        name="Unisex Staple T-Shirt | Bella + Canvas 3001",
        description="Een comfortabel en stijlvol shirt.",
        printful_product_id=71,
        base_price=15.95,
        additional_price_per_area=5.00
    )
    db.session.add(product1)

    variant1 = Variant(
        product=product1,
        printful_variant_id=4012, # Zwart, Maat L
        color="Black Heather",
        size="L",
        price=24.95,
        merch_color_type="dark",
        available_regions=["Europe", "USA"],
        is_active=True,
        print_areas={
            "front": { "name": "Front", "image_url": "/images/unisex-staple-t-shirt-black-heather-front.png" },
            "back": { "name": "Back", "image_url": "/images/unisex-staple-t-shirt-black-heather-back.png" }
        }
    )
    db.session.add(variant1)

    db.session.commit()
    print("Testproduct succesvol toegevoegd!")

# In app.py (zorg dat 'import json' bovenaan staat)

@app.cli.command("sync-printful")
def sync_printful_command():
    """DEBUG: Haalt de ruwe data voor de eerste product template op en print deze."""
    print("--- DEBUG MODE: Ruwe data ophalen van Printful ---")
    API_KEY = os.environ.get('PRINTFUL_API_KEY')
    if not API_KEY:
        print("Error: PRINTFUL_API_KEY is niet ingesteld.")
        return
        
    headers = {'Authorization': f'Bearer {API_KEY}'}

    try:
        # Haal de lijst met templates op
        templates_response = requests.get('https://api.printful.com/product-templates', headers=headers)
        templates_response.raise_for_status()
        templates_data = templates_response.json().get('result', {})
        templates = templates_data.get('items', [])
        
        if not templates:
            print("Geen product-templates gevonden in je Printful account.")
            return

        # Pak de eerste de beste template voor deze test
        first_template = templates[0]
        product_id = first_template.get('product_id')
        print(f"Template gevonden. Details ophalen voor product ID: {product_id}...")

        # Haal de details op voor dat ene product
        details_response = requests.get(f'https://api.printful.com/products/{product_id}', headers=headers)
        details_response.raise_for_status()
        full_details = details_response.json()
        
        # Print de volledige, opgemaakte JSON response
        print("\n--- VOLLEDIGE RUWE DATA VAN PRINTFUL ---")
        print(json.dumps(full_details, indent=2))
        print("----------------------------------------")
        
        print("\nDebug-script voltooid. Kopieer de JSON-output hierboven.")

    except requests.exceptions.RequestException as e:
        print(f"Fout bij communicatie met Printful: {e}")
    except Exception as e:
        print(f"Onverwachte fout: {e}")