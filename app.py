from flask import Flask, jsonify
from dotenv import load_dotenv
from config import Config
from models import User, Product, Variant, Design, Order, PrintArea
from routes.auth import auth_bp
from routes.api import api_bp
from flask_migrate import Migrate
from extensions import db, cors
from admin import setup_admin
import os
import click
import requests
from extensions import db, cors
from admin import setup_admin

load_dotenv()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, origins=["https://miles-to-merch.vercel.app", "http://localhost:8081"], supports_credentials=True)
    setup_admin(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    @app.route('/')
    def index():
        return jsonify({'message': 'Welcome!'})
    return app

app = create_app()

def slugify(text):
    if not text: return ""
    text = text.lower()
    text = re.sub(r'[\s/\|]+', '-', text)
    text = re.sub(r'[^\w\-]', '', text)
    return text

def get_color_type_from_name(color_name):
    dark_keywords = ['black', 'charcoal', 'navy', 'dark', 'forest', 'maroon', 'burgundy']
    if color_name is None: return 'light'
    for keyword in dark_keywords:
        if keyword in color_name.lower():
            return 'dark'
    return 'light'

@app.cli.command("seed-db")
def seed_db_command():
    """Reset en vult de database met test Print Areas."""
    db.drop_all()
    db.create_all()
    print("Database is gereset.")

    # Voeg een testproduct toe
    product1 = Product(name="Unisex Staple T-Shirt | Bella + Canvas 3001", printful_product_id=71)
    db.session.add(product1)
    
    # Voeg de printvlakken voor dit product toe
    print_areas_data = [
        PrintArea(product=product1, placement='front', name='Grote Print Voorkant', price=5.95, width=900, height=1200, top=200, left=550, mockup_width=2000, mockup_height=2000),
        PrintArea(product=product1, placement='back', name='Grote Print Achterkant', price=5.95, width=900, height=1200, top=200, left=550, mockup_width=2000, mockup_height=2000),
        PrintArea(product=product1, placement='sleeve_left', name='Linkermouw', price=2.20, width=200, height=200, top=400, left=150, mockup_width=2000, mockup_height=2000),
        PrintArea(product=product1, placement='sleeve_right', name='Rechtermouw', price=2.20, width=200, height=200, top=400, left=1650, mockup_width=2000, mockup_height=2000),
    ]
    db.session.add_all(print_areas_data)
    db.session.commit()
    print("Testproduct succesvol toegevoegd!")

# In app.py

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
            product_details = details_response.json().get('result', {})
            product_data = product_details.get('product', {})
            variants_data = product_details.get('variants', [])
            
            # --- NIEUWE LOGICA VOOR MOCKUP URLS ---
            # Extract alle mockup URLs uit de hoofd "files" van het product.
            # We maken een dictionary die we later kunnen gebruiken om te matchen.
            product_files = product_data.get('files', [])
            mockup_urls_by_variant_id = {}
            for file_info in product_files:
                if file_info.get('type') == 'mockup' and file_info.get('placement') == 'front':
                    # De Printful API linkt mockup files aan de variant_ids die ze vertegenwoordigen
                    for variant_id_str in file_info.get('variant_ids', []):
                        variant_id = int(variant_id_str)
                        if variant_id not in mockup_urls_by_variant_id: # Pak de eerste geschikte mockup
                            mockup_urls_by_variant_id[variant_id] = file_info.get('preview_url')
            # --- EINDE NIEUWE LOGICA ---

            db_product = Product.query.filter_by(printful_product_id=template_product_id).first()
            if not db_product:
                db_product = Product(
                    name=product_data.get('title', template_product_name),
                    description=product_data.get('description'),
                    printful_product_id=template_product_id,
                    base_price=float(variants_data[0].get('price', 0.0)) if variants_data else 0.0
                )
                db.session.add(db_product)
                db.session.commit()
                print(f"Nieuw product aangemaakt: {db_product.name}")

            variants_processed = 0
            for p_variant in variants_data:
                p_variant_id = p_variant.get('id')
                
                db_variant = Variant.query.filter_by(printful_variant_id=p_variant_id).first()
                if not db_variant:
                    db_variant = Variant(
                        product_id=db_product.id,
                        printful_variant_id=p_variant_id,
                        is_active=False # Nieuwe varianten zijn standaard inactief
                    )
                    db.session.add(db_variant)
                
                db_variant.color = p_variant.get('color')
                db_variant.size = p_variant.get('size')
                db_variant.price = float(p_variant.get('price'))
                db_variant.merch_color_type = get_color_type_from_name(p_variant.get('color'))
                db_variant.available_regions = p_variant.get('availability_regions', [])
                
                # --- GEFIXTE MOCKUP URL LOGICA ---
                # Nu halen we de mockup_url uit onze eerder gemaakte dictionary
                mockup_url = mockup_urls_by_variant_id.get(p_variant_id)
                
                # Zorg ervoor dat de print_areas een JSON-structuur blijft
                db_variant.print_areas = {
                    "front": {"name": "Front", "image_url": mockup_url}
                    # Voeg hier meer placements toe als Printful die aanbiedt en je ze wilt opslaan
                }
                # --- EINDE GEFIXTE MOCKUP URL LOGICA ---

                variants_processed += 1
            
            db.session.commit()
            print(f"{variants_processed} varianten verwerkt voor {db_product.name}.")
            print(f"...Klaar met template {template_product_name}.")

    except requests.exceptions.RequestException as e:
        print(f"Fout bij communicatie met Printful: {e}")
        db.session.rollback()
    except Exception as e:
        print(f"Onverwachte fout tijdens synchronisatie: {e}")
        db.session.rollback()

    print("\nSynchronisatie voltooid!")