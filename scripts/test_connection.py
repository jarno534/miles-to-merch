import os
from dotenv import load_dotenv
import psycopg2

# Force reload of .env
load_dotenv(override=True)

url = os.environ.get('DATABASE_URL')
print(f"Testing connection to: {url}")

try:
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    print("SUCCESS: Connection established and query executed!")
    conn.close()
except Exception as e:
    print(f"FAILURE: {e}")
