import sqlite3
import bcrypt

# Connect to the database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Create the database
def setup_database():
    # Create the client table if it doesn't already exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS client (
        client_id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_forename VARCHAR(50),
        client_surname VARCHAR(50),
        client_DOB DATE,
        client_gender VARCHAR(6),
        client_phone VARCHAR(15),
        client_email VARCHAR(50),
        client_address VARCHAR(100),
        client_comments VARCHAR(100)
    )
    ''')

    # Create the staff table if it doesn't already exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS staff (
        staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
        staff_forename VARCHAR(50),
        staff_surname VARCHAR(50),
        staff_DOB DATE,
        staff_gender VARCHAR(9),
        staff_phone VARCHAR(15),
        staff_email VARCHAR(50),
        staff_address VARCHAR(100),
        staff_status VARCHAR(20),
        staff_comments VARCHAR(100)
    )
    ''')

    # Create the service table if it doesn't already exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS service (
        service_id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_name VARCHAR(50),
        service_cost FLOAT,
        service_length INTEGER
    )
    ''')

    # Create the appointment table if it doesn't already exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS appointment (
        appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        staff_id INTEGER,
        service_id INTEGER,
        appointment_session_time TIME,
        appointment_session_date DATE,
        appointment_status VARCHAR(9),
        appointment_comments VARCHAR(100)
    )
    ''')

    # Create the login table if it doesn't already exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS login (
        staff_id INTEGER,
        username VARCHAR(30) PRIMARY KEY UNIQUE,
        password VARCHAR(50)
    )
    ''')

    # Create the bill table if it doesn't already exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bill (
        bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id INTEGER,
        bill_amount FLOAT,
        bill_status VARCHAR(20)
    )
    ''')
    # Commit these changes to the database
    conn.commit()

# Add a default password on first load up
def add_default_admin():
    default_password = b"Password1"  
    # This encrypts the password so it is not stored as plain text
    hashed_password = bcrypt.hashpw(default_password, bcrypt.gensalt())

    # Insert into the login table the Admin account, with a default password and an ID of 1
    cursor.execute("INSERT OR IGNORE INTO login (staff_id, username, password) VALUES (?, ?, ?)",
                   (1, "Admin", hashed_password))

    # Commit this change to the database
    conn.commit()

# Run the program
if __name__ == "__main__":
    # Set up the database tables
    setup_database()
    # Add the default admin account
    add_default_admin()
    # Close the database connection
    conn.close()
    # Print a message to let the user know that the setup is finished
    print("Database setup Completed")