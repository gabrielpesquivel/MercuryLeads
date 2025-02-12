import sqlite3

# Connect to (or create) the contacts.db file
conn = sqlite3.connect('contacts.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Drop existing tables to start fresh
cursor.execute("DROP TABLE IF EXISTS contacts;")
cursor.execute("DROP TABLE IF EXISTS projects;")

# Create the projects table first (since contacts reference projects)
cursor.execute('''
    CREATE TABLE projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        organisation TEXT NOT NULL,
        city TEXT,
        install_target TEXT,
        action_required TEXT
    );
''')

# Create the contacts table with a foreign key to the projects table
cursor.execute('''
    CREATE TABLE contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        last_contacted TEXT,
        project_id INTEGER,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
    );
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database rebuilt: contacts.db with 'contacts' and 'projects' tables initialized.")
