from flask import Flask, jsonify, session
from dotenv import load_dotenv
from config import Config
from models import User, Product, Variant, PrintArea, Design, Order
from routes.auth import auth_bp
from routes.api import api_bp
from flask_migrate import Migrate
import os
from admin import setup_admin
from extensions import db, cors

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
    @app.route('/debug-session')
    def debug_session():
        try:
            session_content = str(dict(session))
            return session_content
        except Exception as e:
            return f"Fout bij het lezen van de sessie: {e}"
    return app

app = create_app()


from commands import register_commands
register_commands(app)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
