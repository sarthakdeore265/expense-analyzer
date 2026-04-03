import streamlit as st

def get_db_connection():
    # Streamlit manages the connection pool automatically
    return st.connection("postgresql", type="sql")

def create_table():
    conn = get_db_connection()
    with conn.session as session:
        session.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id SERIAL PRIMARY KEY,
                date TEXT,
                category TEXT,
                amount REAL,
                description TEXT
            );
        """)
        session.commit()
