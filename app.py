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

    # We hebben nu de tokens! Voor nu printen we ze alleen maar
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    expires_at = token_data.get("expires_at")

    return f"Authorization successful!<br>Access Token: {access_token}<br>Refresh Token: {refresh_token}<br>Expires At: {expires_at}"

if __name__ == "__main__":
    app.run(port=5000)