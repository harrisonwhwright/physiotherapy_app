import sqlite3
import bcrypt

def setup_database():
    conn = sqlite3.connect("physiotherapy.db")
    cursor = conn.cursor()

    # Create tables if they don't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY,
            client_id INTEGER,
            staff_id INTEGER,
            session_time TEXT,
            session_date TEXT,
            status TEXT,
            comments TEXT,
            FOREIGN KEY(client_id) REFERENCES clients(id),
            FOREIGN KEY(staff_id) REFERENCES staff(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY,
            forename TEXT,
            surname TEXT,
            dob TEXT,
            gender TEXT,
            phone TEXT,
            email TEXT,
            comments TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            forename TEXT,
            surname TEXT,
            password TEXT,
            access_level TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY,
            item_name TEXT,
            quantity INTEGER,
            expiry_date TEXT,
            supplier TEXT,
            cost_price REAL
        )
    """)

    # Add default admin user
    default_password = b"Password1"  
    hashed_password = bcrypt.hashpw(default_password, bcrypt.gensalt())

    cursor.execute("INSERT OR IGNORE INTO staff (username, password, forename, surname, access_level) VALUES (?, ?, ?, ?, ?)",
                   ("Admin", hashed_password, "Admin", "User", "admin"))

    # Commit the changes
    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_database()
