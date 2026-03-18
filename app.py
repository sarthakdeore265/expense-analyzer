import streamlit as st
import pandas as pd
import os

from database import create_table
from expense_manager import add_expense, get_expenses
from ml_model import predict_spending

# Page config (must be FIRST Streamlit command)
st.set_page_config(page_title="Expense Analyzer", layout="wide")

# Initialize DB
if not os.path.exists("expenses.db"):
    create_table()

st.title("💰 Smart Expense Analyzer")

# Add Expense Section
st.header("➕ Add Expense")

date = st.date_input("Date")
category = st.selectbox("Category", ["Food", "Travel", "Shopping", "Bills", "Other"])
amount = st.number_input("Amount")
description = st.text_input("Description")

if st.button("Add Expense"):
    add_expense(str(date), category, amount, description)
    st.success("Expense Added!")

# Dashboard Section
st.header("📊 Expense Dashboard")

df = get_expenses()

if df is not None and not df.empty:
    st.write(df)

    # Category-wise spending
    st.subheader("Category-wise Spending")
    category_data = df.groupby("category")["amount"].sum()
    st.bar_chart(category_data)

    # Monthly spending
    st.subheader("Monthly Spending")
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')
    monthly = df.groupby('month')['amount'].sum()
    st.line_chart(monthly)

    # Alerts
    st.subheader("⚠ Alerts")
    if category_data.max() > 5000:
        st.warning("You overspent in one category!")

    # Prediction
    st.subheader("🔮 Next Month Prediction")
    prediction = predict_spending(df)
    st.write(f"Expected Spending: ₹{prediction}")

else:
    st.info("No data yet. Add some expenses!")
    menu = ["Dashboard", "Add Expense", "Insights"]
choice = st.sidebar.selectbox("Menu", menu)
if choice == "Add Expense":
    st.header("➕ Add Expense")
    # your input code

elif choice == "Dashboard":
    st.header("📊 Dashboard")
    # charts

elif choice == "Insights":
    st.header("🤖 Insights")
    # prediction + alerts
