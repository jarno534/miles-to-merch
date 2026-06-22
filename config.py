import os
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("Geen SECRET_KEY ingesteld! Voeg deze toe aan de environment variables.")
    # ----------------------------------------------------
    
    _db_url = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'site.db')
    # Render provides 'postgres://' but SQLAlchemy 2.x requires 'postgresql://'
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = _db_url

    # Connection pool settings for Render free tier (handles sleep/wake cycles)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,      # Test connections before use (detects stale connections)
        'pool_recycle': 280,        # Recycle connections every ~4.5 min (Render cuts idle connections at 5 min)
        'pool_timeout': 20,         # Wait max 20s for a connection from pool
        'pool_size': 5,             # Keep 5 connections in pool
        'max_overflow': 2,          # Allow 2 extra connections under load
    }

    # Strava API-instellingen
    STRAVA_CLIENT_ID = os.environ.get('STRAVA_CLIENT_ID')
    STRAVA_CLIENT_SECRET = os.environ.get('STRAVA_CLIENT_SECRET')

    # Printful API Settings
    PRINTFUL_API_KEY = os.environ.get('PRINTFUL_API_KEY')

    # Frontend & Backend URLs
    FRONTEND_URL = os.environ.get('FRONTEND_URL') or 'http://localhost:8081'
    BACKEND_URL = os.environ.get('BACKEND_URL') or 'http://localhost:5000'

    # Session Cookie Settings
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE')
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() in ('true', '1', 't')
    SESSION_COOKIE_DOMAIN = os.environ.get('SESSION_COOKIE_DOMAIN')

    # Stripe
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
