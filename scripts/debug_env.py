import os
from dotenv import load_dotenv

load_dotenv(override=True)

url = os.environ.get('DATABASE_URL')

if url:
    print(f"Loaded length: {len(url)}")
    print(f"Starts with: {url[:15]}")
    print(f"Ends with: {url[-20:]}") # Show the end where sslmode should be
    if '"' in url:
       print("WARNING: URL contains quotes!")
else:
    print("DATABASE_URL is None or Empty")
