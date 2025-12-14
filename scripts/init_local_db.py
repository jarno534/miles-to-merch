from app import create_app, db
from models import User

app = create_app()

with app.app_context():
    print("Creating database tables...")
    db.create_all()
    print("Database tables created successfully!")
    
    # Optional: Verify user count
    count = User.query.count()
    print(f"Current user count: {count}")
