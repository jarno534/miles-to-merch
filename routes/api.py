import requests
from datetime import datetime
from functools import wraps
from flask import Blueprint, jsonify, request, session, current_app
from models import User, Product, Design
from extensions import db

api_bp = Blueprint('api', __name__, url_prefix='/api')

# --- Helper Functies ---

def refresh_strava_token(user):
    """Vernieuwt de Strava access token voor een gegeven gebruiker."""
    if datetime.now().timestamp() > user.expires_at:
        print(f"Token voor gebruiker {user.strava_id} is verlopen. Bezig met vernieuwen.")
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
        print("Token succesvol vernieuwd.")
    return user

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authenticatie vereist.'}), 401
        return f(*args, **kwargs)
    return decorated_function

# --- API Routes ---

@api_bp.route('/activities')
@login_required
def activities():
    user = User.query.get(session['user_id'])
    try:
        user = refresh_strava_token(user)
        headers = {'Authorization': f'Bearer {user.access_token}'}
        params = {'per_page': 200}
        response = requests.get('https://www.strava.com/api/v3/athlete/activities', headers=headers, params=params)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.HTTPError as e:
        return jsonify({'error': f'Fout bij ophalen van Strava-activiteiten: {e}'}), 500

@api_bp.route('/activities/<int:activity_id>')
@login_required
def activity_details(activity_id):
    user = User.query.get(session['user_id'])
    try:
        user = refresh_strava_token(user)
        headers = {'Authorization': f'Bearer {user.access_token}'}
        
        main_res = requests.get(f'https://www.strava.com/api/v3/activities/{activity_id}', headers=headers)
        main_res.raise_for_status()
        
        keys = 'latlng,distance,heartrate,altitude,velocity_smooth,time'
        streams_res = requests.get(f'https://www.strava.com/api/v3/activities/{activity_id}/streams', headers=headers, params={'keys': keys, 'key_by_type': 'true'})
        streams_res.raise_for_status()

        photos_res = requests.get(f'https://www.strava.com/api/v3/activities/{activity_id}/photos', headers=headers, params={'size': 600})
        
        return jsonify({
            'details': main_res.json(), 'streams': streams_res.json(),
            'photos': photos_res.json() if photos_res.ok else []
        })
    except requests.exceptions.HTTPError as e:
        return jsonify({'error': f'Fout bij ophalen van activiteitdetails: {e}'}), 500

@api_bp.route('/products')
def products():
    return jsonify([p.to_dict() for p in Product.query.all()])

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
    user = User.query.get(session['user_id'])
    return jsonify([d.to_dict() for d in user.designs])

@api_bp.route('/designs/<int:design_id>')
@login_required
def get_single_design(design_id):
    """Fetches a single design by its ID."""
    design = Design.query.get_or_404(design_id)
    # Security check: ensure the design belongs to the logged-in user
    if design.user_id != session['user_id']:
        return jsonify({'error': 'Forbidden'}), 403
    return jsonify(design.to_dict())

@api_bp.route('/designs/<int:design_id>', methods=['DELETE'])
@login_required
def delete_design(design_id):
    """Deletes a single design by its ID."""
    design = Design.query.get_or_404(design_id)
    # Security check
    if design.user_id != session['user_id']:
        return jsonify({'error': 'Forbidden'}), 403
    
    db.session.delete(design)
    db.session.commit()
    return jsonify({'message': 'Design deleted successfully'}), 200

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

    # Update fields if they are provided in the request
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    user.shipping_address = data.get('shipping_address', user.shipping_address)
    user.shipping_city = data.get('shipping_city', user.shipping_city)
    user.shipping_zip = data.get('shipping_zip', user.shipping_zip)
    user.shipping_country = data.get('shipping_country', user.shipping_country)

    db.session.commit()
    return jsonify(user.to_dict())