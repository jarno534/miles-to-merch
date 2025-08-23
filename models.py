from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from datetime import datetime

class User(db.Model):
    """User model for storing both local and Strava accounts."""
    id = db.Column(db.Integer, primary_key=True)
    
    # Account Info
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(128), nullable=True)
    name = db.Column(db.String(100), nullable=True) # <-- NEW
    
    # Shipping Info
    shipping_address = db.Column(db.String(200), nullable=True) # <-- NEW
    shipping_city = db.Column(db.String(100), nullable=True)    # <-- NEW
    shipping_zip = db.Column(db.String(20), nullable=True)      # <-- NEW
    shipping_country = db.Column(db.String(100), nullable=True) # <-- NEW

    # Strava Info
    strava_id = db.Column(db.Integer, unique=True, nullable=True)
    access_token = db.Column(db.String(128), nullable=True)
    refresh_token = db.Column(db.String(128), nullable=True)
    expires_at = db.Column(db.Integer, nullable=True)
    
    designs = db.relationship('Design', backref='user', lazy=True)

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

# De Product en Design modellen blijven ongewijzigd
class Product(db.Model):
    # ... (geen wijzigingen hier)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(200), nullable=True)
    price = db.Column(db.Float, nullable=False)
    printful_variant_id = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'description': self.description,
            'image_url': self.image_url, 'price': self.price
        }

class Design(db.Model):
    # ... (geen wijzigingen hier)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    design_data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(100), nullable=False, default="My Design")

    def to_dict(self):
        return {
            'id': self.id, 'user_id': self.user_id, 'product_id': self.product_id,
            'design_data': self.design_data, 'name': self.name,
            'created_at': self.created_at.isoformat()
        }