import os
from flask import Flask, redirect, request
from dotenv import load_dotenv

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
    # This is the endpoint Strava will redirect to
    code = request.args.get("code")
    if code:
        return f"Authorization successful! Code: {code}"
    else:
        return "Authorization failed or was denied."

if __name__ == "__main__":
    app.run(port=5000)