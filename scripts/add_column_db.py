import sqlite3

def add_column():
    conn = sqlite3.connect('instance/site.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE product ADD COLUMN printful_name VARCHAR(255)")
        print("Column 'printful_name' added successfully.")
    except sqlite3.OperationalError as e:
        print(f"Error (maybe column exists): {e}")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_column()
