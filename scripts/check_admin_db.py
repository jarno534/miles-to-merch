import requests

BASE_URL = "http://localhost:5000"
EMAIL = "jarno.blomme@telenet.be"
PASSWORD = "admin" # Assuming user used 'admin' or something common. If this fails, I'll try 'test'.
# User said "Ik heb mijn account verwijderd en terug geregistreerd", implying they set a password.
# I will try to register again just in case, or login.
# Actually, I'll try to LOGIN first. If fail, catch it.

def check_admin():
    session = requests.Session()
    
    # Try logging in
    # User might have used a different password.
    # Since I don't know it, I can't login as them unless I reset it or look at the DB.
    # But I can look at the DB directly since it is SQLite!
    
    from app import create_app
    from models import User
    
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email=EMAIL).first()
        if not user:
            print(f"User {EMAIL} not found in DB!")
            return
            
        print(f"User found: ID={user.id}, Email={user.email}")
        print(f"is_admin in DB: {user.is_admin}")
        
        # Also check to_dict output
        print(f"to_dict output: {user.to_dict()}")

if __name__ == "__main__":
    check_admin()
