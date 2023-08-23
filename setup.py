# setup.py
import sqlite3

def setup_database():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    # Create loginDetails table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS loginDetails (
        username TEXT PRIMARY KEY NOT NULL,
        password TEXT NOT NULL
    )
    """)

    # Create staffDetails table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS staffDetails (
        staffID INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        access_level INTEGER NOT NULL,
        staff_forename TEXT NOT NULL,
        staff_surname TEXT NOT NULL,
        staff_role TEXT NOT NULL,
        DOB TEXT NOT NULL,
        gender TEXT CHECK(gender IN ('Male', 'Female', 'Other')) NOT NULL,
        phone TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL
    )
    """)

    # Create clientDetails table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientDetails (
        clientID INTEGER PRIMARY KEY,
        client_forename TEXT NOT NULL,
        client_surname TEXT NOT NULL,
        DOB TEXT NOT NULL,
        gender TEXT CHECK(gender IN ('Male', 'Female', 'Other')) NOT NULL,
        phone TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        comments TEXT
    )
    """)


    # Create session table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS session (
        sessionID INTEGER PRIMARY KEY,
        clientID INTEGER NOT NULL,
        staffID INTEGER NOT NULL,
        session_datetime TEXT NOT NULL,
        session_status TEXT NOT NULL,
        comments TEXT,
        FOREIGN KEY(clientID) REFERENCES clientDetails(clientID),
        FOREIGN KEY(staffID) REFERENCES staffDetails(staffID)
    )
    """)


    # Create appointments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        sessionID INTEGER NOT NULL,
        clientID INTEGER NOT NULL,
        staffID INTEGER NOT NULL,
        PRIMARY KEY (sessionID, clientID, staffID),
        FOREIGN KEY(sessionID) REFERENCES session(sessionID),
        FOREIGN KEY(clientID) REFERENCES clientDetails(clientID),
        FOREIGN KEY(staffID) REFERENCES staffDetails(staffID)
    )
    """)

    # Create inventory table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        itemID INTEGER PRIMARY KEY,
        itemName TEXT NOT NULL,
        quantity INTEGER CHECK(quantity >= 0) NOT NULL,
        expiraryDate TEXT,
        supplier TEXT NOT NULL,
        cost_price REAL CHECK(cost_price >= 0.0) NOT NULL
    )
    """)

    connection.commit()
    connection.close()

if __name__ == "__main__":
    setup_database()
