from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
import json

class User(db.Model):
    """User model for storing both local and Strava accounts."""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=True)
    name = db.Column(db.String(100), nullable=True)
    shipping_address = db.Column(db.String(200), nullable=True)
    shipping_city = db.Column(db.String(100), nullable=True)
    shipping_zip = db.Column(db.String(20), nullable=True)
    shipping_country = db.Column(db.String(100), nullable=True)
    strava_id = db.Column(db.Integer, unique=True, nullable=True)
    access_token = db.Column(db.String(128), nullable=True)
    refresh_token = db.Column(db.String(128), nullable=True)
    expires_at = db.Column(db.Integer, nullable=True)
    designs = db.relationship('Design', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'shipping_address': self.shipping_address,
            'shipping_city': self.shipping_city,
            'shipping_zip': self.shipping_zip,
            'shipping_country': self.shipping_country,
            'has_strava_linked': self.strava_id is not None
        }

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    printful_product_id = db.Column(db.Integer, unique=True, nullable=False)
    base_price = db.Column(db.Float, nullable=False, default=0.0)
    additional_price_per_area = db.Column(db.Float, nullable=False, default=0.0)
    variants = db.relationship('Variant', backref='product', lazy='dynamic', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'printful_product_id': self.printful_product_id,
            'variants': [v.to_dict() for v in self.variants.filter_by(is_active=True).all()]
        }

class Variant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    
    # Unieke ID's van Printful
    printful_variant_id = db.Column(db.Integer, unique=True, nullable=False)
    
    # Producteigenschappen
    color = db.Column(db.String(50), nullable=False)
    size = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    # Eigenschappen voor de designer
    merch_color_type = db.Column(db.String(10), nullable=False) # 'light' of 'dark'
    print_areas = db.Column(db.JSON, nullable=False)
    
    # Nieuwe velden voor beschikbaarheid en curatie
    available_regions = db.Column(db.JSON, nullable=False) # Slaat een lijst op, bv. ["USA", "EUR"]
    is_active = db.Column(db.Boolean, default=False, nullable=False) # Jij bepaalt of deze te koop is

    def to_dict(self):
        # Haal de eerste mockup afbeelding voor deze variant op
        mockup_url = None
        if self.print_areas and 'front' in self.print_areas:
            mockup_url = self.print_areas['front'].get('image_url')

        return {
            'id': self.id,
            'printful_variant_id': self.printful_variant_id,
            'product_name': self.product.name, # Voeg de algemene productnaam toe
            'color': self.color,
            'size': self.size,
            'price': self.price,
            'merch_color_type': self.merch_color_type,
            'mockup_url': mockup_url,
            'print_areas': self.print_areas
        }

class Design(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    variant_id = db.Column(db.Integer, nullable=True)
    preview_url = db.Column(db.String(255), nullable=True)
    design_data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(100), nullable=False, default="My Design")

    def to_dict(self):
        product_info = self.product.to_dict() if self.product else None
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'variant_id': self.variant_id,
            'preview_url': self.preview_url,
            'design_data': self.design_data,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'product': product_info
        }

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    design_id = db.Column(db.Integer, db.ForeignKey('design.id'), unique=True, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    order_status = db.Column(db.String(50), nullable=False, default='Pending')
    printful_order_id = db.Column(db.Integer, nullable=True)
    printful_order_status = db.Column(db.String(50), nullable=True)
    stripe_session_id = db.Column(db.String(255), unique=True, nullable=True)
    total_price = db.Column(db.Float, nullable=False)
    order_date = db.Column(db.DateTime, server_default=func.now())
    shipping_name = db.Column(db.String(100), nullable=True)
    shipping_address = db.Column(db.String(200), nullable=True)
    shipping_city = db.Column(db.String(100), nullable=True)
    shipping_zip = db.Column(db.String(20), nullable=True)
    shipping_country = db.Column(db.String(100), nullable=True)
    user = db.relationship('User', backref=db.backref('orders', lazy=True, cascade="all, delete-orphan"))
    design = db.relationship('Design', backref=db.backref('order', uselist=False))

    def to_dict(self):
        design_name = self.design.name if self.design else "Unknown Design"
        product_name = self.design.product.name if self.design and self.design.product else "Unknown Product"
        return {
            'id': self.id,
            'order_status': self.order_status,
            'total_price': self.total_price,
            'order_date': self.order_date.isoformat(),
            'design_id': self.design_id,
            'design_name': design_name,
            'product_name': product_name,
        }