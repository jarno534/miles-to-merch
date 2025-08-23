import requests
from flask import Blueprint, redirect, request, session, jsonify, current_app
from models import User
from extensions import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Registers a new user with email and password."""
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email address already in use'}), 409

    user = User(email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    session['user_id'] = user.id
    return jsonify(user.to_dict()), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Logs in a user with email and password."""
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if user is None or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

    session['user_id'] = user.id
    return jsonify(user.to_dict()), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logs the user out."""
    session.pop('user_id', None)
    return jsonify({'message': 'Successfully logged out'}), 200

@auth_bp.route('/status')
def status():
    """Checks the current login status of the user."""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return jsonify({'logged_in': True, 'user': user.to_dict()})
    return jsonify({'logged_in': False}), 401

# --- Strava Specific Routes ---

@auth_bp.route('/login/strava')
def strava_login():
    """Redirects the user to the Strava authentication page."""
    auth_url = (
        f"http://www.strava.com/oauth/authorize?"
        f"client_id={current_app.config['STRAVA_CLIENT_ID']}&"
        f"response_type=code&"
        f"redirect_uri={current_app.config['STRAVA_REDIRECT_URI']}&"
        f"scope=activity:read_all"
    )
    return redirect(auth_url)

@auth_bp.route('/callback')
def strava_callback():
    """Handles the callback from Strava after authentication."""
    code = request.args.get('code')
    if not code:
        return 'Authentication failed: no code received', 400

    # Exchange code for tokens
    token_payload = {
        'client_id': current_app.config['STRAVA_CLIENT_ID'],
        'client_secret': current_app.config['STRAVA_CLIENT_SECRET'],
        'code': code,
        'grant_type': 'authorization_code'
    }
    response = requests.post('https://www.strava.com/oauth/token', data=token_payload)
    response.raise_for_status()
    tokens = response.json()
    
    strava_athlete_id = tokens['athlete']['id']
    
    # Find user by Strava ID
    user = User.query.filter_by(strava_id=strava_athlete_id).first()

    if user:
        # User exists, just update their tokens
        user.access_token = tokens['access_token']
        user.refresh_token = tokens['refresh_token']
        user.expires_at = tokens['expires_at']
    else:
        # No user with this Strava ID exists, create a new one
        user = User(
            strava_id=strava_athlete_id,
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token'],
            expires_at=tokens['expires_at']
        )
        db.session.add(user)
    
    db.session.commit()

    # Log the user in by setting the session
    session['user_id'] = user.id
    
    # Redirect to the frontend activities page
    return redirect('http://localhost:8081/activities')