import streamlit as st
import pandas as pd
from database import get_db_connection

def add_expense(date, category, amount, description):
    conn = get_db_connection()
    with conn.session as session:
        session.execute(
            "INSERT INTO expenses (date, category, amount, description) VALUES (:date, :cat, :amt, :desc)",
            {"date": date, "cat": category, "amt": amount, "desc": description}
        )
        session.commit()

def get_expenses():
    conn = get_db_connection()
    # query() returns a pandas DataFrame automatically
    df = conn.query("SELECT * FROM expenses", ttl=0) # ttl=0 ensures fresh data
    return df
