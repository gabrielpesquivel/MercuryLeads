import sqlite3

# Connect to (or create) the contacts.db file
conn = sqlite3.connect('contacts.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create the contact table with the desired columns
cursor.execute('''
    CREATE TABLE contact (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        last_contacted TEXT
    );
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("contacts.db created and contact table initialized.")
