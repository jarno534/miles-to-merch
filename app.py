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

def ensure_phase3_columns(app):
    """Adds Phase 3 columns to the DB if they don't exist yet.
    This is a safe, idempotent migration that runs on every startup."""
    from sqlalchemy import text, inspect as sa_inspect
    with app.app_context():
        try:
            engine = db.engine
            inspector = sa_inspect(engine)

            variant_cols = [c['name'] for c in inspector.get_columns('variant')]
            if 'print_areas' not in variant_cols:
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE variant ADD COLUMN print_areas JSON"))
                    conn.commit()
                print("DB migration: Added print_areas to variant.")

            product_cols = [c['name'] for c in inspector.get_columns('product')]
            if 'sponsored_settings' not in product_cols:
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE product ADD COLUMN sponsored_settings JSON"))
                    conn.commit()
                print("DB migration: Added sponsored_settings to product.")

        except Exception as e:
            print(f"WARNING: ensure_phase3_columns failed (may be OK): {e}")

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, origins=["https://miles-to-merch.vercel.app", "http://localhost:8081"], supports_credentials=True)
    setup_admin(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    ensure_phase3_columns(app)
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
    @app.route('/debug-products')
    def debug_products():
        import traceback
        try:
            from models import Product
            products = Product.query.all()
            result = []
            for p in products:
                try:
                    d = p.to_dict()
                    result.append({'id': p.id, 'name': p.name, 'ok': True})
                except Exception as e2:
                    result.append({'id': p.id, 'name': p.name, 'error': str(e2)})
            return jsonify({'count': len(products), 'products': result})
        except Exception as e:
            return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

    return app

app = create_app()


from commands import register_commands
register_commands(app)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
