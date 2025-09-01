from flask import Flask, jsonify
from dotenv import load_dotenv
from config import Config
from models import User, Product, Design, Order
from routes.auth import auth_bp
from routes.api import api_bp
from flask_migrate import Migrate
import os
import click
import json
from routes.admin import admin_bp
from extensions import db

load_dotenv()
migrate = Migrate()

def create_app(config_class=Config):
    """Factory function to create the Flask app."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)

    @app.route('/')
    def index():
        return jsonify({'message': 'Welcome to the API! Go to /auth/login/strava to begin.'})

    @app.cli.command("seed-db")
    @click.option('--reseed', is_flag=True, help='Verwijdert alle data en vult de database opnieuw.')
    def seed_db_command(reseed):
        """Vult de database met initiële data na het (optioneel) resetten."""
        if reseed:
            print("Verwijderen van alle tabellen en opnieuw aanmaken...")
            db.drop_all()
            db.create_all()
            print("Database is gereset.")

        # Voorkom duplicaten als de database al bestaat en --reseed niet is gebruikt
        if Product.query.first() is not None:
            print("Database bevat al producten. Seeden wordt overgeslagen.")
            return

        print("Database vullen met producten...")
        
        products_data = [
            {
                "id": 1,
                "name": "Unisex Staple T-Shirt | Bella + Canvas 3001",
                "description": "Een comfortabel en stijlvol shirt, perfect voor elke gelegenheid.",
                "price": 24.95,
                "printful_product_id": 71,
                "printful_variant_id": 4012,
                "print_areas": json.dumps({
                    "front": {
                        "name": "Front",
                        "image_url": "/images/unisex-staple-t-shirt-black-heather-front.png",
                        "width": 900, "height": 1200, "top": 200, "left": 550,
                        "mockup_width": 2000,
                        "mockup_height": 2000
                    },
                    "back": {
                        "name": "Back",
                        "image_url": "/images/unisex-staple-t-shirt-black-heather-back.png",
                        "width": 900, "height": 1200, "top": 200, "left": 550,
                        "mockup_width": 2000,
                        "mockup_height": 2000
                    }
                })
            }
        ]

        for prod_data in products_data:
            # Controleer of het product al bestaat voordat je het toevoegt
            if not Product.query.get(prod_data['id']):
                new_product = Product(**prod_data)
                db.session.add(new_product)

        db.session.commit()
        print("Producten succesvol toegevoegd aan de database!")

    @app.after_request
    def after_request(response):
        """Voegt de CORS-headers toe aan elke response."""
        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:8081')
        response.headers.add('Access-Control-Allow-Origin', frontend_url)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
