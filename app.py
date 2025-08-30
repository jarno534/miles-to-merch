from flask import Flask, jsonify
from dotenv import load_dotenv
from config import Config
from extensions import db, cors
from models import Product 
from routes.auth import auth_bp
from routes.api import api_bp
from flask_migrate import Migrate
import os

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

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # We definiëren de toegestane origins expliciet.
    allowed_origins = [
        "http://localhost:8081", 
        "https://miles-to-merch.vercel.app"
    ]
    cors.init_app(app, supports_credentials=True, origins=allowed_origins)
    # --- EINDE VAN DE CORRECTIE ---

    # Registreer blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    @app.route('/')
    def index():
        return jsonify({'message': 'Welcome to the API! Go to /auth/login/strava to begin.'})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
