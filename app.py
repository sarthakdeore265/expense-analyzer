import streamlit as st
import pandas as pd
from database import create_table
from expense_manager import add_expense, get_expenses
from ml_model import predict_spending

st.set_page_config(page_title="NexFin Vercel", layout="wide")

# Ensure table exists in Postgres
create_table()

st.title("💰 Smart Expense Analyzer")

# Input Section
with st.sidebar:
    st.header("➕ Add Expense")
    date = st.date_input("Date")
    category = st.selectbox("Category", ["Food", "Travel", "Shopping", "Bills", "Other"])
    amount = st.number_input("Amount", min_value=0.0)
    description = st.text_input("Description")

    if st.button("Add Expense"):
        add_expense(str(date), category, amount, description)
        st.success("Expense Saved to Cloud!")

# Dashboard
df = get_expenses()

if not df.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Recent Transactions")
        st.dataframe(df.tail(10))
    
    with col2:
        st.subheader("Category Breakdown")
        cat_total = df.groupby("category")["amount"].sum()
        st.bar_chart(cat_total)

    # ML Prediction
    st.divider()
    prediction = predict_spending(df)
    st.metric("Predicted Next Month Spending", f"${prediction}")
else:
    st.info("Add some expenses to see your cloud-synced dashboard.")
