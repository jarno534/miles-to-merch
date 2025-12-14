import requests
import json

def test_register():
    url = "http://localhost:5000/auth/register"
    headers = {"Content-Type": "application/json"}
    data = {
        "email": "test_script_user@example.com",
        "password": "securepassword123",
        "name": "Script User"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_register()
