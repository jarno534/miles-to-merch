import requests
import json
from datetime import datetime
from functools import wraps
from flask import Blueprint, jsonify, request, session, current_app, url_for
from models import User, Product, Variant, Design, Order
from extensions import db
import base64
import os
from uuid import uuid4
import stripe
from utils.gpx_parser import parse_gpx_to_strava_format

api_bp = Blueprint('api', __name__, url_prefix='/api')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required.'}), 401
        return f(*args, **kwargs)
    return decorated_function

    return decorated_function

# --- GPX Upload Route ---
@api_bp.route('/activities/upload-gpx', methods=['POST'])
@login_required
def upload_gpx():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    try:
        activity_data = parse_gpx_to_strava_format(file.stream)
        if not activity_data:
             return jsonify({'error': 'Could not parse GPX file'}), 400
        return jsonify({'details': activity_data})
        
    except Exception as e:
        print(f"GPX Parse Error: {e}")
        return jsonify({'error': 'Invaild GPX file'}), 400

def refresh_strava_token(user):
    if user.expires_at and datetime.now().timestamp() > user.expires_at:
        print(f"Token for user {user.strava_id} has expired. Refreshing.")
        payload = {
            'client_id': current_app.config['STRAVA_CLIENT_ID'],
            'client_secret': current_app.config['STRAVA_CLIENT_SECRET'],
            'grant_type': 'refresh_token',
            'refresh_token': user.refresh_token
        }
        response = requests.post('https://www.strava.com/oauth/token', data=payload)
        response.raise_for_status()
        new_tokens = response.json()
        
        user.access_token = new_tokens['access_token']
        user.refresh_token = new_tokens['refresh_token']
        user.expires_at = new_tokens['expires_at']
        
        db.session.commit()
        print("Token successfully refreshed.")
    return user

# --- Activity Routes ---
@api_bp.route('/activities')
def activities():
    strava_tokens = None
    
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.access_token:
            user = refresh_strava_token(user)
            strava_tokens = {'access_token': user.access_token}
    elif 'strava_guest_data' in session:
        strava_tokens = session['strava_guest_data']

    if not strava_tokens:
        return jsonify({'error': 'Not authenticated with Strava.'}), 401

    try:
        headers = {'Authorization': f'Bearer {strava_tokens["access_token"]}'}
        params = {'per_page': 200}
        response = requests.get('https://www.strava.com/api/v3/athlete/activities', headers=headers, params=params)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.HTTPError as e:
        return jsonify({'error': f'Failed to fetch Strava activities: {e}'}), 500

@api_bp.route('/activities/<int:activity_id>')
def activity_details(activity_id):
    """
    Fetches details for a single activity, for either a logged-in user or a guest.
    """
    if activity_id == 999999:
        return jsonify({
            'details': {
                'id': 999999, 'name': 'Mock Activity with map', 'distance': 5000, 
                'moving_time': 1800, 'elapsed_time': 1800, 'total_elevation_gain': 50,
                'elev_high': 100, 'average_speed': 2.7, 'max_speed': 5.0,
                'average_heartrate': 140, 'max_heartrate': 160, 
                'start_date': datetime.now().isoformat(),
                'start_latlng': [52.3676, 4.9041], # Amsterdam
                'map': {'summary_polyline': 'u`t~H{z_]a@'},
                'athlete': {'id': 123, 'sex': 'M'}
            },
            'streams': {
                'latlng': {'data': [[52.3676, 4.9041], [52.3702, 4.8952]]},
                'distance': {'data': [0, 5000]},
                'altitude': {'data': [0, 5]},
                'time': {'data': [0, 1800]}
            },
            'photos': []
        })

    strava_tokens = None
    
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.access_token:
            user = refresh_strava_token(user)
            strava_tokens = {'access_token': user.access_token}
    elif 'strava_guest_data' in session:
        strava_tokens = session['strava_guest_data']

    if not strava_tokens:
        return jsonify({'error': 'Not authenticated with Strava.'}), 401

    try:
        headers = {'Authorization': f'Bearer {strava_tokens["access_token"]}'}
        
        main_res = requests.get(f'https://www.strava.com/api/v3/activities/{activity_id}', headers=headers)
        main_res.raise_for_status()
        
        keys = 'time,distance,latlng,distance,altitude,velocity_smooth,heartrate,cadence,watts,temp,moving,grade_smooth'
        streams_res = requests.get(f'https://www.strava.com/api/v3/activities/{activity_id}/streams', headers=headers, params={'keys': keys, 'key_by_type': 'true'})
        streams_res.raise_for_status()

        photos_res = requests.get(f'https://www.strava.com/api/v3/activities/{activity_id}/photos', headers=headers, params={'size': 600})
        
        return jsonify({
            'details': main_res.json(), 
            'streams': streams_res.json(),
            'photos': photos_res.json() if photos_res.ok else []
        })
    except requests.exceptions.HTTPError as e:
        return jsonify({'error': f'Failed to fetch activity details: {e}'}), 500

# --- Product Routes ---
@api_bp.route('/products')
def products():
    try:
        products = Product.query.all()
        # Filter products that have at least one active variant
        valid_products = []
        for p in products:
            p_dict = p.to_dict()
            if p_dict['variants'] and len(p_dict['variants']) > 0:
                valid_products.append(p_dict)
                
        return jsonify(valid_products)
    except Exception as e:
        print(f"ERROR in /api/products: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/admin/products')
@login_required
def admin_products():
    """Fetches all products including inactive variants for admin use."""
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        return jsonify({'error': 'Admin privileges required'}), 403
        
    try:
        products = Product.query.all()
        # Pass include_inactive=True
        return jsonify([p.to_dict(include_inactive=True) for p in products])
    except Exception as e:
        print(f"ERROR in /api/admin/products: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/products/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        return jsonify({'error': 'Forbidden'}), 403

    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
        
    db.session.commit()
    return jsonify(product.to_dict(include_inactive=True))

@api_bp.route('/products/<int:product_id>/price', methods=['PUT'])
@login_required
def update_product_price(product_id):
    """Updates the price for ALL variants of a product."""
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        return jsonify({'error': 'Forbidden'}), 403

    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    new_price = data.get('price')
    if new_price is None:
        return jsonify({'error': 'Price is required'}), 400
        
    try:
        # Update all variants
        # Using bulk update via relationship might be cleaner but iterating is safe
        for variant in product.variants.all():
            variant.price = float(new_price)
            
        db.session.commit()
        return jsonify({'message': 'Prices updated successfully', 'product': product.to_dict(include_inactive=True)})
    except ValueError:
        return jsonify({'error': 'Invalid price format'}), 400

@api_bp.route('/variants/<int:variant_id>', methods=['PUT'])
@login_required
def update_variant(variant_id):
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        return jsonify({'error': 'Forbidden'}), 403

    variant = db.session.query(Variant).get_or_404(variant_id)
    data = request.get_json()
    
    if 'is_active' in data:
        variant.is_active = bool(data['is_active'])
        
    db.session.commit()
    return jsonify(variant.to_dict())

# --- Printful Catalog Integration ---

@api_bp.route('/printful/catalog')
@login_required
def get_printful_catalog():
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        return jsonify({'error': 'Forbidden'}), 403
        
    api_key = os.environ.get('PRINTFUL_API_KEY')
    if not api_key:
        return jsonify({'error': 'API Key missing'}), 500
        
    try:
        # Fetch all products from Printful Catalog
        res = requests.get('https://api.printful.com/products', headers={'Authorization': f'Bearer {api_key}'})
        res.raise_for_status()
        data = res.json()
        return jsonify(data.get('result', []))
    except Exception as e:
        print(f"Printful Catalog Error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/printful/catalog/<int:printful_id>')
@login_required
def get_printful_catalog_details(printful_id):
    """Fetches details (description, price) for a specific Printful product."""
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        return jsonify({'error': 'Forbidden'}), 403
        
    api_key = os.environ.get('PRINTFUL_API_KEY')
    headers = {'Authorization': f'Bearer {api_key}'}
    try:
        res = requests.get(f'https://api.printful.com/products/{printful_id}', headers=headers)
        res.raise_for_status()
        data = res.json().get('result', {})
        product = data.get('product', {})
        variants = data.get('variants', [])
        
        # Get price range or first variant price
        price = "N/A"
        if variants:
            price = variants[0].get('price', 'N/A')
            
        return jsonify({
            'description': product.get('description'),
            'price': price
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/products/import', methods=['POST'])
@login_required
def import_product():
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        return jsonify({'error': 'Forbidden'}), 403
        
    data = request.get_json()
    printful_id = data.get('printful_id')
    
    if not printful_id:
        return jsonify({'error': 'printful_id required'}), 400
        
    # Check if already exists
    if Product.query.filter_by(printful_product_id=printful_id).first():
        return jsonify({'error': 'Product already exists'}), 409
        
    api_key = os.environ.get('PRINTFUL_API_KEY')
    headers = {'Authorization': f'Bearer {api_key}'}
    
    try:
        # 1. Fetch Details
        res = requests.get(f'https://api.printful.com/products/{printful_id}', headers=headers)
        res.raise_for_status()
        prod_data = res.json().get('result', {}).get('product', {})
        variants_data = res.json().get('result', {}).get('variants', [])
        
        # 2. Create Product
        new_product = Product(
            name=prod_data.get('title'),
            printful_name=prod_data.get('title'),
            description=prod_data.get('description', '')[:500] if prod_data.get('description') else '',
            printful_product_id=printful_id,
            product_image_url=prod_data.get('image')
        )
        db.session.add(new_product)
        db.session.flush() # Get ID
        
        # 3. Create Variants
        for v_data in variants_data:
            # Simple color type logic
            color_name = (v_data.get('color') or '').lower()
            merch_type = 'dark' if any(x in color_name for x in ['black', 'navy', 'dark', 'heather']) else 'light'
            
            # Default price (placeholder)
            base_price = 25.00
            
            variant = Variant(
                product_id=new_product.id,
                printful_variant_id=v_data.get('id'),
                color=v_data.get('color') or 'Unknown',
                color_code=v_data.get('color_code'),
                size=v_data.get('size') or 'One Size',
                price=base_price,
                merch_color_type=merch_type,
                image=v_data.get('image'),
                image_base_path=None, 
                available_regions=["EU", "US"],
                is_active=False
            )
            variant.image_urls = {'mockup': v_data.get('image')}
            db.session.add(variant)
            
        db.session.commit()
        return jsonify({'message': 'Imported', 'product': new_product.to_dict(include_inactive=True)})
        
    except Exception as e:
        db.session.rollback()
        print(f"Import Error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/products/<int:product_id>', methods=['GET'])
def get_single_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())

@api_bp.route('/products/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        return jsonify({'error': 'Forbidden'}), 403

    product = Product.query.get_or_404(product_id)
    
    # Optional: Check for designs/orders to prevent accidental data loss of history
    # For now, we allow deletion as requested.
    
    try:
        # Variants should cascade delete if set up in models, otherwise manual:
        Variant.query.filter_by(product_id=product.id).delete()
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/products/<int:product_id>/printful-details')
def get_printful_product_details(product_id):
    """Haalt alle varianten (kleuren, maten) op van een specifiek Printful product."""
    product = Product.query.get_or_404(product_id)
    if not product.printful_product_id:
        return jsonify({'error': 'Product does not have a Printful ID'}), 404

    printful_api_key = current_app.config.get('PRINTFUL_API_KEY')
    if not printful_api_key:
        return jsonify({'error': 'Printful API key not configured'}), 500

    headers = {'Authorization': f'Bearer {printful_api_key}'}
    url = f'https://api.printful.com/products/{product.printful_product_id}'

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json().get('result', {})
        
        # We sturen de varianten en mockups door naar de frontend
        return jsonify({
            'variants': data.get('variants', []),
            'mockups': data.get('mockups', []) 
        })
    except requests.exceptions.RequestException as e:
        error_message = f"Failed to fetch Printful details: {e}"
        if e.response:
            error_message += f" | Status: {e.response.status_code} | Response: {e.response.text}"
        print(error_message)
        return jsonify({'error': 'Failed to communicate with Printful.'}), 502

# --- Design Routes ---
@api_bp.route('/designs', methods=['POST'])
@login_required
def create_design():
    data = request.get_json()
    if not data or 'product_id' not in data or 'design_data' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    design_data = data['design_data']
    preview_images = data.get('preview_images', {})
    
    # Backward compatibility: Check if preview_images is just one key/value or mixed
    # Frontend now sends: preview_images = { 'front': 'data:...' }
    
    preview_urls = {}
    
    base_url = current_app.config.get('BACKEND_URL', '').rstrip('/')
    upload_folder = os.path.join(current_app.static_folder, 'uploads', 'designs')
    os.makedirs(upload_folder, exist_ok=True)

    for view, b64_data in preview_images.items():
        if not b64_data: 
            continue
        try:
            if "," in b64_data:
                header, encoded = b64_data.split(",", 1)
            else:
                encoded = b64_data
                
            image_data = base64.b64decode(encoded)
            filename = f"{uuid4().hex}_{view}.png"
            filepath = os.path.join(upload_folder, filename)
            
            with open(filepath, "wb") as f:
                f.write(image_data)
                
            preview_urls[view] = f"{base_url}/static/uploads/designs/{filename}"
            print(f"DEBUG: Saved preview for {view}: {preview_urls[view]}")
            
        except Exception as e:
            print(f"DEBUG: Failed to save preview for {view}. Error: {e}")

    # Fallback/Legacy handling if preview_image (singular) is in design_data
    if 'preview_image' in design_data:
        # Avoid saving it in DB as massive string
        legacy_img = design_data.pop('preview_image')
        # If we didn't get preview_images, try to save this one as 'front'
        if not preview_urls:
             try:
                if "," in legacy_img:
                    header, encoded = legacy_img.split(",", 1)
                else:
                    encoded = legacy_img
                image_data = base64.b64decode(encoded)
                filename = f"{uuid4().hex}_legacy.png"
                filepath = os.path.join(upload_folder, filename)
                with open(filepath, "wb") as f:
                    f.write(image_data)
                preview_urls['front'] = f"{base_url}/static/uploads/designs/{filename}"
             except Exception as e:
                print(f"Legacy image save failed: {e}")

    new_design = Design(
        user_id=session['user_id'],
        product_id=data['product_id'],
        variant_id=data.get('variant_id'),
        design_data=design_data,
        preview_urls=preview_urls, # Using the JSON column
        name=data.get('name', 'Mijn Ontwerp')
    )
    db.session.add(new_design)
    db.session.commit()

    return jsonify(new_design.to_dict()), 201

@api_bp.route('/designs')
@login_required
def get_designs():
    """Fetches all designs for the logged-in user, sorted by most recent first."""
    user_id = session['user_id']
    
    designs = Design.query.filter_by(user_id=user_id).order_by(Design.created_at.desc()).all()
    
    return jsonify([d.to_dict() for d in designs])

@api_bp.route('/designs/<int:design_id>')
@login_required
def get_single_design(design_id):
    """Fetches a single design by its ID."""
    design = Design.query.get_or_404(design_id)
    if design.user_id != session['user_id']:
        return jsonify({'error': 'Forbidden'}), 403
    return jsonify(design.to_dict())

@api_bp.route('/designs/<int:design_id>', methods=['DELETE'])
@login_required
def delete_design(design_id):
    """Deletes a single design by its ID."""
    design = Design.query.get_or_404(design_id)
    if design.user_id != session['user_id']:
        return jsonify({'error': 'Forbidden'}), 403
    
    db.session.delete(design)
    db.session.commit()
    return jsonify({'message': 'Design deleted successfully'}), 200

@api_bp.route('/designs/<int:design_id>', methods=['PUT'])
@login_required
def update_design(design_id):
    """Updates a design's name."""
    design = Design.query.get_or_404(design_id)
    
    if design.user_id != session['user_id']:
        return jsonify({'error': 'Forbidden'}), 403

    data = request.get_json()
    new_name = data.get('name')

    if not new_name or len(new_name.strip()) == 0:
        return jsonify({'error': 'A valid name is required'}), 400

    design.name = new_name.strip()
    db.session.commit()
    
    return jsonify(design.to_dict())

# --- Profile Routes ---
@api_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Gets the current logged-in user's profile data."""
    user = User.query.get(session['user_id'])
    return jsonify(user.to_dict())

@api_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Updates the current logged-in user's profile data."""
    user = User.query.get(session['user_id'])
    data = request.get_json()

    new_email = data.get('email')
    if new_email and new_email != user.email:
        existing_user = User.query.filter(User.email == new_email, User.id != user.id).first()
        if existing_user:
            return jsonify({'error': 'Email address is already in use by another account.'}), 409
        user.email = new_email

    user.name = data.get('name', user.name)
    user.shipping_address = data.get('shipping_address', user.shipping_address)
    user.shipping_city = data.get('shipping_city', user.shipping_city)
    user.shipping_zip = data.get('shipping_zip', user.shipping_zip)
    user.shipping_country = data.get('shipping_country', user.shipping_country)

    if 'password' in data and data['password']:
        user.set_password(data['password'])

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error updating profile: {e}")
        return jsonify({'error': 'An internal error occurred while saving.'}), 500
        
    return jsonify(user.to_dict())

@api_bp.route('/profile/delete', methods=['POST'])
@login_required
def delete_profile_with_password():
    """Deletes the current user after verifying their password."""
    user = User.query.get(session['user_id'])
    data = request.get_json()
    password = data.get('password')

    if not password or not user.check_password(password):
        return jsonify({'error': 'Incorrect password'}), 401

    db.session.delete(user)
    db.session.commit()
    
    session.clear()
    
    return jsonify({'message': 'Account deleted successfully'}), 200

@api_bp.route('/athlete-stats/<int:athlete_id>')
@login_required
def get_athlete_stats(athlete_id):
    """
    Haalt de all-time statistieken voor een specifieke atleet op.
    """
    user = User.query.get(session['user_id'])
    if not user or not user.access_token:
        return jsonify({'error': 'Not authenticated with Strava.'}), 401

    user = refresh_strava_token(user)
    
    try:
        headers = {'Authorization': f'Bearer {user.access_token}'}

        response = requests.get(f'https://www.strava.com/api/v3/athletes/{athlete_id}/stats', headers=headers)
        response.raise_for_status()

        return jsonify(response.json())

    except requests.exceptions.HTTPError as e:
        return jsonify({'error': f'Failed to fetch Strava athlete stats: {e}'}), 500

# --- Order Routes ---
@api_bp.route('/orders', methods=['GET'])
@login_required
def get_orders():
    """Fetches all orders for the logged-in user."""
    user = User.query.get(session['user_id'])
    # Sorteer de bestellingen direct via de relatie
    orders = sorted(user.orders, key=lambda o: o.order_date, reverse=True)
    
    orders_data = []
    for order in orders:
        order_dict = order.to_dict()
        
        # Gebruik de relaties, dit is veel efficiënter en veiliger
        if order.design and order.design.product:
            product = order.design.product
            order_dict['product_name'] = product.name
            
            # Haal de afbeelding veilig op
            image_url = None
            if product.print_areas and isinstance(product.print_areas, dict) and product.print_areas:
                # Gebruik 'front' als die bestaat, anders de eerste de beste
                first_area_key = 'front' if 'front' in product.print_areas else list(product.print_areas.keys())[0]
                image_url = product.print_areas[first_area_key].get('image_url')
            
            order_dict['product_image_url'] = image_url

        else:
            # Vangnet voor als een product of design niet gevonden wordt
            order_dict['product_name'] = "Product Not Found"
            order_dict['product_image_url'] = None

        orders_data.append(order_dict)
            
    return jsonify(orders_data)

@api_bp.route('/orders/<int:order_id>', methods=['GET'])
@login_required
def get_single_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != session['user_id']:
        return jsonify({'error': 'Forbidden'}), 403

    order_data = order.to_dict()
    design = Design.query.get(order.design_id)
    if design and design.product:
        order_data['product_name'] = design.product.name
        if design.product.print_areas:
            first_area_key = list(design.product.print_areas.keys())[0]
            order_data['product_image_url'] = design.product.print_areas[first_area_key]['image_url']
        else:
            order_data['product_image_url'] = None

    return jsonify(order_data)

# --- Checkout Route ---
@api_bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    """Creëert een Stripe Checkout sessie en geeft de ID terug."""
    data = request.get_json()
    design_id = data.get('design_id')
    quantity = data.get('quantity', 1)

    if not design_id:
        return jsonify({'error': 'Design ID is required'}), 400

    design = Design.query.get_or_404(design_id)
    
    # Ownership Check
    if design.user_id != session['user_id']:
        return jsonify({'error': 'Unauthorized access to this design'}), 403

    if not design.product:
        return jsonify({'error': 'Product not found for this design'}), 404

    product = design.product
    user = User.query.get(session['user_id'])
    
    # Validation: Ensure User has Email and Shipping Address
    missing_fields = []
    if not user.email: missing_fields.append('email')
    if not user.shipping_address: missing_fields.append('shipping_address')
    if not user.shipping_city: missing_fields.append('shipping_city')
    if not user.shipping_zip: missing_fields.append('shipping_zip')
    if not user.shipping_country: missing_fields.append('shipping_country')
    
    if missing_fields:
        return jsonify({
            'error': 'Profile incomplete. Please provide shipping details.',
            'missing_fields': missing_fields,
            'code': 'PROFILE_INCOMPLETE'
        }), 400

    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    frontend_url = current_app.config['FRONTEND_URL']

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card', 'bancontact'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': product.name,
                        'description': f'Custom design: "{design.name}"',
                    },
                    'unit_amount': int(product.price * 100),
                },
                'quantity': quantity,
            }],
            mode='payment',
            success_url=f"{frontend_url}/order/confirmation/{{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{frontend_url}/checkout/{design.id}",
            metadata={
                'user_id': session['user_id'],
                'design_id': design.id,
                'quantity': quantity
            }
        )
        return jsonify({'id': checkout_session.id})

    except Exception as e:
        print(f"Stripe Error: {e}")
        return jsonify({'error': 'Could not create payment session.'}), 500

@api_bp.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = current_app.config['STRIPE_WEBHOOK_SECRET']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return jsonify(status='invalid payload'), 400
    except stripe.error.SignatureVerificationError as e:
        return jsonify(status='invalid signature'), 400

    if event['type'] == 'checkout.session.completed':
        session_data = event['data']['object']
        metadata = session_data.get('metadata', {})
        user_id = metadata.get('user_id')
        design_id = metadata.get('design_id')
        quantity = int(metadata.get('quantity', 1))

        if not user_id or not design_id:
            print("Webhook Error: user_id or design_id missing in metadata")
            return jsonify(status='error', reason='missing metadata'), 400

        user = User.query.get(user_id)
        design = Design.query.get(design_id)
        product = design.product

        if not all([user, design, product]):
            print("Webhook Error: User, design, or product not found")
            return jsonify(status='error', reason='data not found'), 400

        shipping_details = session_data.get('shipping_details')
        if not shipping_details or not shipping_details.get('address'):
             print(f"Webhook Error: Shipping details missing from Stripe session {session_data.get('id')}")
             return jsonify(status='error', reason='shipping details missing'), 400
        
        address = shipping_details.get('address', {})

        new_order = Order(
            user_id=user.id,
            design_id=design.id,
            total_price=product.price * quantity,
            shipping_name=shipping_details.get('name', user.name),
            shipping_address=address.get('line1'),
            shipping_city=address.get('city'),
            shipping_zip=address.get('postal_code'),
            shipping_country=address.get('country'),
            order_status='Paid',
            stripe_session_id=session_data.get('id')
        )
        db.session.add(new_order)
        db.session.commit()
 
        printful_api_key = current_app.config['PRINTFUL_API_KEY']
        headers = {
            'Authorization': f'Bearer {printful_api_key}'
        }
        printful_payload = {
            'confirm': False,
            'recipient': { 
                'name': new_order.shipping_name, 
                'address1': new_order.shipping_address, 
                'city': new_order.shipping_city, 
                'zip': new_order.shipping_zip, 
                'country_code': new_order.shipping_country
            },
            'items': [{
                'variant_id': design.variant_id,
                'quantity': quantity,
                'files': [{'url': design.preview_url}]
            }]
        }

        try:
            store_id = current_app.config.get('PRINTFUL_STORE_ID')
            response = requests.post(f'https://api.printful.com/stores/{store_id}/orders', headers=headers, json=printful_payload)
            response.raise_for_status()
            printful_order_data = response.json().get('result', {})

            new_order.printful_order_id = printful_order_data.get('id')
            new_order.printful_order_status = printful_order_data.get('status')
            new_order.order_status = 'Submitted to Printful'
            db.session.commit()
            print("Successfully submitted order to Printful.")

        except requests.exceptions.RequestException as e:
            print(f"Printful API Error after payment: {e}")
            new_order.order_status = 'Payment successful, Printful submission failed'
            db.session.commit()

    return jsonify(status='success'), 200

@api_bp.route('/order-by-session/<session_id>')
@login_required
def get_order_by_session_id(session_id):
    order = Order.query.filter_by(stripe_session_id=session_id, user_id=session['user_id']).first_or_404()

    order_data = order.to_dict()
    if order.design and order.design.product:
        product = order.design.product
        image_url = None
        if product.print_areas and isinstance(product.print_areas, dict) and product.print_areas:
            first_area_key = 'front' if 'front' in product.print_areas else list(product.print_areas.keys())[0]
            image_url = product.print_areas[first_area_key].get('image_url')
        order_data['product_image_url'] = image_url

    return jsonify(order_data)