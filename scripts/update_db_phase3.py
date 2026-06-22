
import sqlite3
import os

# Path to DB
DB_PATH = os.path.join("instance", "site.db")

def add_columns():
    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Add print_areas to Variant
    try:
        print("Adding print_areas to variant...")
        cursor.execute("ALTER TABLE variant ADD COLUMN print_areas JSON")
        print("   Success.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("   Column already exists.")
        else:
            print(f"   Error: {e}")

    # 2. Add sponsored_settings to Product
    try:
        print("Adding sponsored_settings to product...")
        cursor.execute("ALTER TABLE product ADD COLUMN sponsored_settings JSON")
        print("   Success.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("   Column already exists.")
        else:
            print(f"   Error: {e}")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
    else:
        add_columns()
