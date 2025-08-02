import os
from flask import Flask, redirect, request
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, instance_relative_config=True)

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

    # Wissel de autorisatiecode in voor een access_token
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

    access_token = token_data.get("access_token")

    # Nu gebruiken we de access_token om de atleetgegevens op te vragen
    athlete_url = "https://www.strava.com/api/v3/athlete"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    athlete_response = requests.get(athlete_url, headers=headers)
    athlete_data = athlete_response.json()

    if athlete_response.status_code != 200:
        return f"Error fetching athlete data: {athlete_data.get('message', 'Unknown error')}", 500

    return athlete_data

if __name__ == "__main__":
    app.run(port=5000)