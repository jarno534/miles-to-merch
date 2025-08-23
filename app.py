from flask import Flask, jsonify
from dotenv import load_dotenv
from config import Config
from extensions import db, cors
from models import Product 
from routes.auth import auth_bp
from routes.api import api_bp

load_dotenv()


def create_app(config_class=Config):
    """Factory-functie om de Flask-app te maken."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialiseer extensies
    db.init_app(app)
    cors.init_app(app, 
                  supports_credentials=True, 
                  origins=["http://localhost:8081", "https://miles-to-merch.vercel.app"])

    # Registreer blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    with app.app_context():
        db.create_all()
        # Voeg standaardproducten toe als de database leeg is
        if not Product.query.first():
            print("Database is leeg, standaardproducten worden toegevoegd.")
            products_to_add = [
                Product(name="Koffiemok", description="Een mooie mok voor je koffie na het fietsen.", price=14.95, image_url="https://placehold.co/600x400/EEE/31343C?text=Koffiemok"),
                Product(name="T-shirt", description="Een comfortabel shirt met je prestatie.", price=24.95, image_url="https://placehold.co/600x400/EEE/31343C?text=T-shirt"),
                Product(name="Poster", description="Hang je rit aan de muur.", price=19.95, image_url="https://placehold.co/600x400/EEE/31343C?text=Poster")
            ]
            db.session.add_all(products_to_add)
            db.session.commit()

    @app.route('/')
    def index():
        return jsonify({'message': 'Welkom bij de API! Ga naar /auth/login om te beginnen.'})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
