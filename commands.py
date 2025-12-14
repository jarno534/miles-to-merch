import click
import os
import requests
from extensions import db
from models import Product, Variant, PrintArea

def get_color_type_from_name(color_name):
    dark_keywords = ['black', 'charcoal', 'navy', 'dark', 'forest', 'maroon', 'burgundy']
    if color_name is None: return 'light'
    for keyword in dark_keywords:
        if keyword in color_name.lower():
            return 'dark'
    return 'light'

def register_commands(app):
    @app.cli.command("seed-db")
    def seed_db_command():
        """Maakt de catalogus leeg en vult deze met initiële PrintArea data."""
        print("Leegmaken van Variant, PrintArea, en Product tabellen...")
        db.session.query(Variant).delete()
        db.session.query(PrintArea).delete()
        db.session.query(Product).delete()
        db.session.commit()
        print("Catalogus is leeg.")

        db.session.commit()
        print("Catalogus is leeg. Gebruik de Admin Panel om producten toe te voegen via Printful.")

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
            templates_response = requests.get('https://api.printful.com/product-templates', headers=headers)
            templates_response.raise_for_status()
            templates_data = templates_response.json().get('result', {})
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
                
                db_product = Product.query.filter_by(printful_product_id=template_product_id).first()
                if not db_product:
                    db_product = Product(
                        name=product_data.get('title', template_product_name),
                        description=product_data.get('description'),
                        printful_product_id=template_product_id,
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
                            is_active=False
                        )
                        db.session.add(db_variant)

                    db_variant.color = p_variant.get('color')
                    db_variant.color_code = p_variant.get('color_code')
                    db_variant.size = p_variant.get('size')
                    db_variant.price = float(p_variant.get('price'))
                    db_variant.merch_color_type = get_color_type_from_name(p_variant.get('color'))
                    db_variant.available_regions = list(p_variant.get('availability_regions', {}).keys())
                    db_variant.image = p_variant.get('image')
                    mockup_url = p_variant.get('image')
                    db_variant.image_urls = {'default': mockup_url}

                    variants_processed += 1

                db.session.commit()
                print(f"{variants_processed} varianten verwerkt voor {db_product.name}.")

        except requests.exceptions.RequestException as e:
            print(f"Fout bij communicatie met Printful: {e}")
            db.session.rollback()
        except Exception as e:
            print(f"Onverwachte fout tijdens synchronisatie: {e}")
            db.session.rollback()

        print("\nSynchronisatie voltooid!")
