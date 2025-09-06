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

@app.cli.command("sync-printful")
def sync_printful_command():
    """Haalt product templates op van Printful en synchroniseert de database."""
    print("Start synchronisatie met Printful Product Templates...")
    API_KEY = os.environ.get('PRINTFUL_API_KEY')
    if not API_KEY:
        print("Error: PRINTFUL_API_KEY is niet ingesteld.")
        return
        
    headers = {'Authorization': f'Bearer {API_KEY}'}

    try:
        response = requests.get('https://api.printful.com/product-templates', headers=headers)
        response.raise_for_status()
        
        templates_data = response.json().get('result', {})
        templates = templates_data.get('items', [])
        
        print(f"{len(templates)} product-templates gevonden.")

        if not templates:
            print("Geen templates gevonden. Maak eerst een template aan in je Printful dashboard.")
            return

        for template in templates:
            template_product_id = template.get('product_id')
            template_product_name = template.get('title') or "Unnamed Product"
            
            print(f"\nVerwerken van template: {template_product_name} (Product ID: {template_product_id})")

            details_response = requests.get(f'https://api.printful.com/products/{template_product_id}', headers=headers)
            details_response.raise_for_status()
            product_details = details_response.json().get('result', {}).get('product', {})
            variants = details_response.json().get('result', {}).get('variants', [])
            
            db_product = Product.query.filter_by(printful_product_id=template_product_id).first()
            if not db_product:
                db_product = Product(
                    name=product_details.get('title', template_product_name),
                    description=product_details.get('description'),
                    printful_product_id=template_product_id,
                    base_price=float(variants[0].get('price', 0.0)) if variants else 0.0
                )
                db.session.add(db_product)
                db.session.commit() 
                print(f"Nieuw product aangemaakt: {db_product.name}")

            variants_processed = 0
            for p_variant in variants:
                p_variant_id = p_variant.get('id')
                
                db_variant = Variant.query.filter_by(printful_variant_id=p_variant_id).first()
                if not db_variant:
                    db_variant = Variant(
                        product_id=db_product.id,
                        printful_variant_id=p_variant_id,
                        is_active=False
                    )
                    db.session.add(db_variant)
                
                db_variant.color = p_variant.get('color')
                db_variant.size = p_variant.get('size')
                db_variant.price = float(p_variant.get('price'))
                db_variant.merch_color_type = get_color_type_from_name(p_variant.get('color'))
                db_variant.available_regions = p_variant.get('availability_regions', [])
                mockup_url = None
                for file_info in p_variant.get('files', []):
                    if file_info.get('type') == 'mockup' and file_info.get('placement') == 'front':
                        mockup_url = file_info.get('preview_url')
                        break
                if not mockup_url:
                    mockup_url = p_variant.get('product', {}).get('image')

                db_variant.print_areas = {
                    "front": {"name": "Front", "image_url": mockup_url}
                }
                db_variant.print_areas = {
                    "front": {"name": "Front", "image_url": p_variant.get('product', {}).get('image')},
                }
                variants_processed += 1
            
            db.session.commit()
            print(f"{variants_processed} varianten verwerkt voor {db_product.name}.")
            print(f"...Klaar met template {template_product_name}.")

    except requests.exceptions.RequestException as e:
        print(f"Fout bij communicatie met Printful: {e}")
        db.session.rollback()

    print("\nSynchronisatie voltooid!")