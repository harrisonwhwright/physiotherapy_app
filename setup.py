import sqlite3
import bcrypt

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

def setup_database():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS client (
        client_id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_forename VARCHAR(50),
        client_surname VARCHAR(50),
        client_DOB DATE,
        client_gender CHAR(1),
        client_phone VARCHAR(15),
        client_email VARCHAR(50),
        client_address VARCHAR(100),
        client_comments VARCHAR(100)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS staff (
        staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
        staff_forename VARCHAR(50),
        staff_surname VARCHAR(50),
        staff_DOB DATE,
        staff_gender CHAR(1),
        staff_phone VARCHAR(15),
        staff_email VARCHAR(50),
        staff_address VARCHAR(100),
        staff_status VARCHAR(20),
        staff_comments VARCHAR(100)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS service (
        service_id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_name VARCHAR(50),
        service_cost DECIMAL,
        service_typical_length INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS appointment (
        appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER REFERENCES client (client_id),
        staff_id INTEGER REFERENCES staff (staff_id),
        service_id INTEGER REFERENCES service (service_id),
        appointment_session_time TIME,
        appointment_session_date DATE,
        appointment_status VARCHAR(9),
        appointment_comments VARCHAR(100)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS login (
        staff_id INTEGER REFERENCES staff (staff_id),
        username VARCHAR(30) PRIMARY KEY,
        password VARCHAR(50)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bill (
        bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id INTEGER REFERENCES appointment (appointment_id),
        bill_date DATE,
        bill_amount DECIMAL,
        bill_status VARCHAR(20)
    )
    ''')

    conn.commit()

def add_default_admin():
    default_password = b"Password1"  
    hashed_password = bcrypt.hashpw(default_password, bcrypt.gensalt())

    cursor.execute("INSERT OR IGNORE INTO login (staff_id, username, password) VALUES (?, ?, ?)",
                   (1, "Admin", hashed_password))

    conn.commit()

if __name__ == "__main__":
    setup_database()
    add_default_admin()
    conn.close()
    print("Database setup Completed")