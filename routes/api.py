import requests
import json
from datetime import datetime
from functools import wraps
from flask import Blueprint, jsonify, request, session, current_app, url_for
from models import User, Product, Design, Order
from extensions import db
import base64
import os
from uuid import uuid4
import stripe

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
    preview_image_b64 = design_data.pop('preview_image', None)

    preview_url = None
    if preview_image_b64:
        try:
            header, encoded = preview_image_b64.split(",", 1)
            image_data = base64.b64decode(encoded)

            filename = f"{uuid4().hex}.png"

            upload_folder = os.path.join(current_app.static_folder, 'uploads', 'designs')
            os.makedirs(upload_folder, exist_ok=True)

            filepath = os.path.join(upload_folder, filename)
            with open(filepath, "wb") as f:
                f.write(image_data)

            base_url = current_app.config.get('BACKEND_URL', '').rstrip('/')
            preview_url = f"{base_url}/static/uploads/designs/{filename}"

            print(f"DEBUG: Afbeelding opgeslagen. Publieke URL voor Printful is: {preview_url}")

        except Exception as e:
            print(f"DEBUG: Kon afbeelding niet opslaan. Fout: {e}")

    new_design = Design(
        user_id=session['user_id'],
        product_id=data['product_id'],
        variant_id=data.get('variant_id'),
        design_data=design_data,
        preview_url=preview_url,
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

    if not design_id:
        return jsonify({'error': 'Design ID is required'}), 400

    design = Design.query.get_or_404(design_id)
    if not design.product:
        return jsonify({'error': 'Product not found for this design'}), 404

    product = design.product

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
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{frontend_url}/order/confirmation/{{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{frontend_url}/checkout/{design.id}",
            metadata={
                'user_id': session['user_id'],
                'design_id': design.id
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
            total_price=product.price,
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
            'recipient': { 
                'name': new_order.shipping_name, 
                'address1': new_order.shipping_address, 
                'city': new_order.shipping_city, 
                'zip': new_order.shipping_zip, 
                'country_code': new_order.shipping_country
            },
            'items': [{
                'variant_id': design.variant_id,
                'quantity': 1,
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