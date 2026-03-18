import sqlite3

def connect_db():
    conn = sqlite3.connect("expenses.db")
    return conn

def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        category TEXT,
        amount REAL,
        description TEXT
    )
    """)
    
    conn.commit()
    conn.close()
