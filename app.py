import os
from flask import Flask, redirect, request
from dotenv import load_dotenv
import requests
from flask_sqlalchemy import SQLAlchemy
import json

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, instance_relative_config=True)

# Configureer de database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Definieer het databasemodel voor atleten
class Athlete(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    athlete_id = db.Column(db.Integer, unique=True, nullable=False)
    access_token = db.Column(db.String(255), nullable=False)
    refresh_token = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.Integer, nullable=False)

def __repr__(self):
    return f"Athlete('{self.athlete_id}')"

# Strava API credentials from .env
STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")

# Check if credentials are loaded
if not STRAVA_CLIENT_ID or not STRAVA_CLIENT_SECRET:
    raise ValueError("Strava API credentials are not set in the .env file.")

# Strava OAuth URLs
STRAVA_AUTH_URL = "https://www.strava.com/oauth/authorize"
REDIRECT_URI = "http://localhost:5000/strava/callback"

@app.route("/")
def index():
    # Redirect to Strava for authorization
    auth_url = (f"{STRAVA_AUTH_URL}?"
                f"client_id={STRAVA_CLIENT_ID}&"
                f"response_type=code&"
                f"redirect_uri={REDIRECT_URI}&"
                f"approval_prompt=force&"
                f"scope=activity:read_all")
    return redirect(auth_url)

@app.route("/strava/callback")
def strava_callback():
    code = request.args.get("code")

    if not code:
        return "Authorization failed or was denied.", 400

    # Wissel code in voor token
    token_url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code"
    }
    response = requests.post(token_url, data=payload)
    token_data = response.json()

    if response.status_code != 200:
        return f"Error while exchanging code for token: {token_data.get('message', 'Unknown error')}", 500

    # Haal de tokens en atleet-ID op
    athlete_id = token_data['athlete']['id']
    access_token = token_data['access_token']
    refresh_token = token_data['refresh_token']
    expires_at = token_data['expires_at']

    # Sla de gegevens van de atleet op in de database
    athlete = Athlete.query.filter_by(athlete_id=athlete_id).first()
    if athlete:
        athlete.access_token = access_token
        athlete.refresh_token = refresh_token
        athlete.expires_at = expires_at
    else:
        new_athlete = Athlete(athlete_id=athlete_id, access_token=access_token, refresh_token=refresh_token, expires_at=expires_at)
        db.session.add(new_athlete)

    db.session.commit()

    # Gebruik de access_token om de activiteiten van de atleet op te vragen
    activities_url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {access_token}"}

    activities_response = requests.get(activities_url, headers=headers)
    activities_data = activities_response.json()

    if activities_response.status_code != 200:
        return f"Error fetching activities: {activities_data.get('message', 'Unknown error')}", 500

    # Maak een simpele HTML-pagina om de activiteiten weer te geven
    output = "<h1>Your Recent Strava Activities</h1>"
    output += "<ul>"
    for activity in activities_data:
        name = activity.get('name')
        distance_meters = activity.get('distance')
        distance_km = round(distance_meters / 1000, 2)
        activity_type = activity.get('type')
            
        output += f"<li><strong>{name}</strong> - {distance_km} km ({activity_type})</li>"
    output += "</ul>"

    return output

if __name__ == "__main__":
    app.run(port=5000)