from app import app
import traceback

print("Testing mock activity endpoint...")
try:
    with app.test_request_context():
        from routes.api import activity_details
        response = activity_details(999999)
        print("Status Code:", response.status_code)
        print("Response:", response.get_json())
except Exception:
    traceback.print_exc()
