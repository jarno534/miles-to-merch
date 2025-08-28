import requests
from flask import Blueprint, redirect, request, session, jsonify, current_app
from models import User
from extensions import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# In routes/auth.py

@auth_bp.route('/register', methods=['POST'])
def register():
    print("--- Register function started ---")
    try:
        data = request.get_json()
        print(f"1. Data received: {data}")

        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400

        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email address already in use'}), 409

        user = User(email=data['email'])
        print("2. User object created in memory.")
        
        user.set_password(data['password'])
        print("3. Password has been set.")

        # This logic links a Strava guest session if it exists
        if 'strava_guest_data' in session:
            guest_data = session.pop('strava_guest_data')
            user.strava_id = guest_data['strava_id']
            user.access_token = guest_data['access_token']
            user.refresh_token = guest_data['refresh_token']
            user.expires_at = guest_data['expires_at']
            print("4. Linked Strava guest data to new user.")

        db.session.add(user)
        print("5. User added to session.")
        
        print("6. About to commit to database...")
        db.session.commit()
        print("7. Commit successful!")

        session['user_id'] = user.id
        print("8. User ID added to session. Registration complete.")
        return jsonify(user.to_dict()), 201
    except Exception as e:
        print(f"!!! AN ERROR OCCURRED: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred.'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Logs in a user with email and password."""
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if user is None or user.password_hash is None or not user.check_password(data['password']):
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
    # Store the 'next' parameter in the session if it exists
    next_url = request.args.get('next')
    if next_url:
        session['strava_redirect_next'] = next_url

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
    """Handles the callback from Strava."""
    # ... (de code voor het uitwisselen van de token en het updaten van de gebruiker blijft exact hetzelfde) ...
    code = request.args.get('code')
    if not code:
        return 'Authentication failed: no code received', 400

    token_payload = {
        'client_id': current_app.config['STRAVA_CLIENT_ID'],
        'client_secret': current_app.config['STRAVA_CLIENT_SECRET'],
        'code': code,
        'grant_type': 'authorization_code'
    }
    response = requests.post('https://www.strava.com/oauth/token', data=token_payload)
    if not response.ok:
        return 'Error exchanging code for Strava token.', 500
    tokens = response.json()
    
    strava_athlete_id = tokens['athlete']['id']

    if 'user_id' in session:
        current_user = User.query.get(session['user_id'])
        current_user.strava_id = strava_athlete_id
        current_user.access_token = tokens['access_token']
        current_user.refresh_token = tokens['refresh_token']
        current_user.expires_at = tokens['expires_at']
        db.session.commit()
    else:
        session['strava_guest_data'] = {
            'strava_id': strava_athlete_id,
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token'],
            'expires_at': tokens['expires_at']
        }
    
    # --- DIT IS DE BELANGRIJKE WIJZIGING ---
    # Check for a redirect URL stored in the session and remove it
    next_url = session.pop('strava_redirect_next', None)
    if next_url == 'profile':
        return redirect('http://localhost:8081/profile')
    
    # Default redirect for the design flow
    return redirect('http://localhost:8081/activities')
    """
    Handles the callback from Strava.
    - If a user is logged in, it LINKS the Strava account to their existing account.
    - If no user is logged in, it creates a temporary GUEST session.
    """
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
    if not response.ok:
        return 'Error exchanging code for Strava token.', 500
    tokens = response.json()
    
    strava_athlete_id = tokens['athlete']['id']

    # Check if a user is already logged into our site
    if 'user_id' in session:
        # User is logged in, so we are LINKING this Strava account
        current_user = User.query.get(session['user_id'])
        current_user.strava_id = strava_athlete_id
        current_user.access_token = tokens['access_token']
        current_user.refresh_token = tokens['refresh_token']
        current_user.expires_at = tokens['expires_at']
        db.session.commit()
    else:
        # User is NOT logged in, create a GUEST session
        session['strava_guest_data'] = {
            'strava_id': strava_athlete_id,
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token'],
            'expires_at': tokens['expires_at']
        }
    
    # Redirect to the frontend activities page
    return redirect('http://localhost:8081/activities')