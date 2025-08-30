import requests
import json
from datetime import datetime
from functools import wraps
from flask import Blueprint, jsonify, request, session, current_app
from models import User, Product, Design, Order
from extensions import db

api_bp = Blueprint('api', __name__, url_prefix='/api')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required.'}), 401
        return f(*args, **kwargs)
    return decorated_function

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
    return jsonify([p.to_dict() for p in Product.query.all()])

@api_bp.route('/products/<int:product_id>')
def get_single_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())

# In api.py

@api_bp.route('/products/<int:product_id>/printful-details')
def get_printful_product_details(product_id):
    """
    Fetches detailed product information from Printful, including
    variants, mockup images, and print area specifications.
    """
    product = Product.query.get_or_404(product_id)
    if not product.printful_product_id:
        return jsonify({'error': 'Product is not configured for Printful'}), 404

    printful_api_key = current_app.config.get('PRINTFUL_API_KEY')
    if not printful_api_key:
        return jsonify({'error': 'Printful API key is not configured'}), 500
    
    headers = {'Authorization': f'Bearer {printful_api_key}'}
    
    try:
        url = f'https://api.printful.com/products/{product.printful_product_id}'
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        result = data.get('result', {})
        
        variants_info = result.get('variants', [])
        product_info = result.get('product', {})

        # --- NIEUWE, GERICHTE LOGICA ---
        front_template_url = None
        front_template_width = None
        front_template_height = None
        
        if product_info and product_info.get('files'):
            # We zoeken specifiek naar het 'file' object met type 'front'
            for file_info in product_info.get('files'):
                if file_info.get('type') == 'front':
                    # Dit is de juiste template voor de editor!
                    front_template_url = file_info.get('preview_url')
                    front_template_width = file_info.get('width')
                    front_template_height = file_info.get('height')
                    break # Stop met zoeken zodra we het hebben gevonden

        # Veilige fallback: als we om een of andere reden de template niet vinden,
        # gebruiken we de foto met het model om een crash te voorkomen.
        if not front_template_url and variants_info:
            front_template_url = variants_info[0].get('image')

        filtered_data = {
            'variants': variants_info,
            'print_areas': {
                'front': {
                    'url': front_template_url,
                    'width': front_template_width,
                    'height': front_template_height
                }
                # Je kunt hier een vergelijkbare logica voor 'back' toevoegen
            }
        }
        
        return jsonify(filtered_data)

    except requests.exceptions.RequestException as e:
        error_message = f"Failed to fetch product details from Printful: {e}"
        if e.response:
            error_message += f" | Response: {e.response.text}"
        print(error_message)
        return jsonify({'error': 'Failed to fetch product details from Printful.'}), 502

# --- Design Routes ---
@api_bp.route('/designs', methods=['POST'])
@login_required
def create_design():
    data = request.get_json()
    if not data or 'product_id' not in data or 'design_data' not in data:
        return jsonify({'error': 'Ongeldige data. Vereist: product_id, design_data'}), 400

    new_design = Design(
        user_id=session['user_id'], product_id=data['product_id'],
        design_data=data['design_data'], name=data.get('name', 'Mijn Ontwerp')
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

    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    user.shipping_address = data.get('shipping_address', user.shipping_address)
    user.shipping_city = data.get('shipping_city', user.shipping_city)
    user.shipping_zip = data.get('shipping_zip', user.shipping_zip)
    user.shipping_country = data.get('shipping_country', user.shipping_country)

    db.session.commit()
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
@login_required # Zorg ervoor dat de gebruiker is ingelogd
def get_athlete_stats(athlete_id):
    """
    Haalt de all-time statistieken voor een specifieke atleet op.
    """
    user = User.query.get(session['user_id'])
    if not user or not user.access_token:
        return jsonify({'error': 'Not authenticated with Strava.'}), 401

    # Zorg ervoor dat het token geldig is
    user = refresh_strava_token(user)
    
    try:
        headers = {'Authorization': f'Bearer {user.access_token}'}
        
        # Dit is de cruciale API-call naar de stats van de atleet
        response = requests.get(f'https://www.strava.com/api/v3/athletes/{athlete_id}/stats', headers=headers)
        response.raise_for_status()
        
        return jsonify(response.json())
        
    except requests.exceptions.HTTPError as e:
        return jsonify({'error': f'Failed to fetch Strava athlete stats: {e}'}), 500

# --- Order Routes ---
@api_bp.route('/orders', methods=['POST'])
@login_required
def create_order():
    """Creates a new order and submits it to Printful."""
    data = request.get_json()
    design_id = data.get('design_id')

    if not design_id:
        return jsonify({'error': 'Design ID is required'}), 400

    user = User.query.get(session['user_id'])
    design = Design.query.get(design_id)
    product = Product.query.get(design.product_id)

    if not design or design.user_id != user.id:
        return jsonify({'error': 'Design not found or not owned by user'}), 404
    
    if hasattr(design, 'order') and design.order:
        return jsonify({'error': 'This design has already been ordered'}), 409

    if not all([user.name, user.shipping_address, user.shipping_city, user.shipping_zip, user.shipping_country]):
        return jsonify({'error': 'User profile is incomplete'}), 400

    product = Product.query.get(design.product_id)
    if not product:
         return jsonify({'error': 'Product associated with design not found'}), 404

    printful_api_key = current_app.config.get('PRINTFUL_API_KEY')
    if not printful_api_key:
        return jsonify({'error': 'Printful API key is not configured on the server.'}), 500

    headers = {
        'Authorization': f'Bearer {printful_api_key}'
    }
    
    design_image_data = design.design_data.get('preview_image')

    printful_payload = {
        'recipient': {
            'name': user.name,
            'address1': user.shipping_address,
            'city': user.shipping_city,
            'zip': user.shipping_zip,
            'country_code': 'BE'
        },
        'items': [
            {
                'variant_id': product.printful_variant_id or 1,
                'quantity': 1,
                'files': [
                    {
                        'type': 'default',
                        'url': design_image_data
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post('https://api.printful.com/orders', headers=headers, json=printful_payload)
        response.raise_for_status()
        printful_order = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Printful API Error: {e.response.text}")
        return jsonify({'error': 'Failed to submit order to Printful.'}), 502

    new_order = Order(
        user_id=user.id,
        design_id=design.id,
        total_price=product.price,
        shipping_name=user.name,
        shipping_address=user.shipping_address,
        shipping_city=user.shipping_city,
        shipping_zip=user.shipping_zip,
        shipping_country=user.shipping_country,
        order_status='Submitted to Printful'
    )

    db.session.add(new_order)
    db.session.commit()

    return jsonify(new_order.to_dict()), 201

@api_bp.route('/orders', methods=['GET'])
@login_required
def get_orders():
    """Fetches all orders for the logged-in user."""
    user = User.query.get(session['user_id'])
    orders = sorted(user.orders, key=lambda o: o.order_date, reverse=True)
    
    orders_data = []
    for order in orders:
        design = Design.query.get(order.design_id)
        product = Product.query.get(design.product_id)
        order_dict = order.to_dict()
        order_dict['product_name'] = product.name
        order_dict['product_image_url'] = product.image_url
        orders_data.append(order_dict)
        
    return jsonify(orders_data)