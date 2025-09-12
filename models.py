from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=True)
    name = db.Column(db.String(100), nullable=True)
    strava_name = db.Column(db.String(100), nullable=True)
    shipping_address = db.Column(db.String(200), nullable=True)
    shipping_city = db.Column(db.String(100), nullable=True)
    shipping_zip = db.Column(db.String(20), nullable=True)
    shipping_country = db.Column(db.String(100), nullable=True)
    strava_id = db.Column(db.Integer, unique=True, nullable=True)
    access_token = db.Column(db.String(128), nullable=True)
    refresh_token = db.Column(db.String(128), nullable=True)
    expires_at = db.Column(db.Integer, nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    designs = db.relationship('Design', backref='user', lazy=True, cascade="all, delete-orphan")
    orders = db.relationship('Order', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id, 'email': self.email, 'name': self.name,
            'shipping_address': self.shipping_address, 'shipping_city': self.shipping_city,
            'shipping_zip': self.shipping_zip, 'shipping_country': self.shipping_country,
            'has_strava_linked': self.strava_id is not None
        }

    def __str__(self):
        return self.email or f"User ID: {self.id}"

    def __repr__(self):
        return f'<User {self.email}>'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    printful_product_id = db.Column(db.Integer, unique=True, nullable=False)
    product_image_url = db.Column(db.String(255), nullable=True)
    variants = db.relationship('Variant', backref='product', lazy='dynamic', cascade="all, delete-orphan")
    print_areas = db.relationship('PrintArea', backref='product', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        active_variants = self.variants.filter_by(is_active=True).all()
        return {
            'id': self.id, 'name': self.name, 'description': self.description,
            'printful_product_id': self.printful_product_id,
            'product_image_url': self.product_image_url,
            'variants': [v.to_dict() for v in active_variants],
            'print_areas': {p.placement: p.to_dict() for p in self.print_areas}
        }

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f'<Product {self.name}>'

class Variant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    printful_variant_id = db.Column(db.Integer, unique=True, nullable=False)
    color = db.Column(db.String(50), nullable=False)
    color_code = db.Column(db.String(20), nullable=True)
    size = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False)
    merch_color_type = db.Column(db.String(10), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    image_urls = db.Column(db.JSON, nullable=True, default=lambda: {"mockup": None, "template": None})
    image_base_path = db.Column(db.String(255), nullable=True)
    available_regions = db.Column(db.JSON, nullable=False)
    is_active = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        return {
            'id': self.id, 'printful_variant_id': self.printful_variant_id,
            'product_name': self.product.name, 'color': self.color,
            'color_code': self.color_code,
            'size': self.size,
            'price': self.price, 'merch_color_type': self.merch_color_type,
            'image': self.image,
            'image_urls': self.image_urls,
            'image_base_path': self.image_base_path
        }

class PrintArea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    placement = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    top = db.Column(db.Integer, nullable=False)
    left = db.Column(db.Integer, nullable=False)
    mockup_width = db.Column(db.Integer, nullable=False)
    mockup_height = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'id': self.id, 'placement': self.placement, 'name': self.name, 'price': self.price,
            'width': self.width, 'height': self.height, 'top': self.top, 'left': self.left,
            'mockup_width': self.mockup_width, 'mockup_height': self.mockup_height,
            'image_url': self.image_url
        }

class Design(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey('variant.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    preview_urls = db.Column(db.JSON, nullable=True)
    design_data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(100), nullable=False, default="My Design")
    variant = db.relationship('Variant')
    product = db.relationship('Product')

    def to_dict(self):
        return {
            'id': self.id, 'user_id': self.user_id, 'variant_id': self.variant_id,
            'preview_urls': self.preview_urls, 'design_data': self.design_data,
            'name': self.name, 'created_at': self.created_at.isoformat(),
            'variant': self.variant.to_dict() if self.variant else None
        }

    def __str__(self):
        return self.name or f"Design ID: {self.id}"

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
    design = db.relationship('Design', backref=db.backref('order', uselist=False))

    def to_dict(self):
        design_name = self.design.name if self.design else "Unknown Design"
        product_name = self.design.product.name if self.design and self.design.product else "Unknown Product"

        product_image_url = None
        if self.design and self.design.preview_urls:
            image_filename = self.design.preview_urls.get('front')
            if image_filename:
                from flask import url_for
                product_image_url = url_for('static', filename=f'uploads/previews/{image_filename}', _external=True)

        return {
            'id': self.id, 'order_status': self.order_status, 'total_price': self.total_price,
            'order_date': self.order_date.isoformat(), 'design_id': self.design_id,
            'design_name': design_name, 'product_name': product_name,
            'product_image_url': product_image_url
        }