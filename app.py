from flask import Flask, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import requests

# Zorg ervoor dat de database-URI correct is
DB_URI = "sqlite:///strava.db"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
CORS(app)  # CORS inschakelen
db = SQLAlchemy(app)

class Athlete(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(255), nullable=False)
    refresh_token = db.Column(db.String(255), nullable=False)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    # Deze route is voor demonstratiedoeleinden
    return "Miles To Merch API"

@app.route("/strava_callback")
def strava_callback():
    code = request.args.get('code')
    if not code:
        return jsonify({"error": "Authorization code not provided"}), 400

    payload = {
        'client_id': 'YOUR_CLIENT_ID',  # Vervang dit door je Client ID
        'client_secret': 'YOUR_CLIENT_SECRET',  # Vervang dit door je Client Secret
        'code': code,
        'grant_type': 'authorization_code'
    }

    response = requests.post("https://www.strava.com/oauth/token", data=payload)
    data = response.json()

    if response.status_code != 200:
        return jsonify({"error": data.get("message", "Strava authorization failed")}), 400

    access_token = data.get('access_token')
    refresh_token = data.get('refresh_token')

    # Bewaar de tokens in de database
    athlete = Athlete.query.first()
    if athlete:
        athlete.access_token = access_token
        athlete.refresh_token = refresh_token
    else:
        new_athlete = Athlete(access_token=access_token, refresh_token=refresh_token)
        db.session.add(new_athlete)

    db.session.commit()

    return redirect(f"http://localhost:8081/activities")

@app.route("/api/tokens")
def get_tokens():
    athlete = Athlete.query.first()
    if athlete:
        return jsonify({
            "access_token": athlete.access_token,
            "refresh_token": athlete.refresh_token
        })
    else:
        return jsonify({"error": "No athlete found in the database."}), 404

@app.route("/api/activities")
def get_activities():
    athlete = Athlete.query.first()
    if not athlete:
        return jsonify({"error": "No athlete found in the database."}), 404

    access_token = athlete.access_token
    
    headers = {'Authorization': f'Bearer {access_token}'}
    strava_url = "https://www.strava.com/api/v3/athlete/activities"
    
    try:
        response = requests.get(strava_url, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
