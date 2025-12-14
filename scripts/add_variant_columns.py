import sqlite3

def add_columns():
    conn = sqlite3.connect('instance/site.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE variant ADD COLUMN printful_price FLOAT")
        print("Column 'printful_price' added.")
    except sqlite3.OperationalError:
        print("Column 'printful_price' likely exists.")

    try:
        cursor.execute("ALTER TABLE variant ADD COLUMN in_stock BOOLEAN DEFAULT 1")
        print("Column 'in_stock' added.")
    except sqlite3.OperationalError:
        print("Column 'in_stock' likely exists.")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_columns()
