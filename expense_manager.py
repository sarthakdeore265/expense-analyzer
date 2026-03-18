import pandas as pd
from database import connect_db

def add_expense(date, category, amount, description):
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)",
        (date, category, amount, description)
    )
    
    conn.commit()
    conn.close()

def get_expenses():
    conn = connect_db()
    
    df = pd.read_sql_query("SELECT * FROM expenses", conn)
    conn.close()
    
    return df