import streamlit as st
import pandas as pd
import os
import sqlite3
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np

# =========================
# 🎨 PAGE CONFIG
# =========================
st.set_page_config(page_title="Smart Expense Analyzer", page_icon="💰", layout="wide")

# =========================
# 🎨 UI STYLE
# =========================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
}
.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
    box-shadow: 0px 4px 20px rgba(0,0,0,0.3);
}
.stButton>button {
    background: linear-gradient(90deg, #22c55e, #4ade80);
    color: black;
    border-radius: 10px;
    font-weight: bold;
}
section[data-testid="stSidebar"] {
    background-color: #020617;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 🗄 DATABASE
# =========================
def create_table():
    conn = sqlite3.connect("expenses.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS expenses
                 (date TEXT, category TEXT, amount REAL, description TEXT)""")
    conn.commit()
    conn.close()

def add_expense(date, category, amount, description):
    conn = sqlite3.connect("expenses.db")
    c = conn.cursor()
    c.execute("INSERT INTO expenses VALUES (?, ?, ?, ?)",
              (date, category, amount, description))
    conn.commit()
    conn.close()

def get_expenses():
    conn = sqlite3.connect("expenses.db")
    df = pd.read_sql("SELECT * FROM expenses", conn)
    conn.close()
    return df

# =========================
# 🤖 ML MODEL
# =========================
def predict_spending(df):
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    df['days'] = (df['date'] - df['date'].min()).dt.days
    X = df[['days']]
    y = df['amount']

    if len(df) < 2:
        return 0

    model = LinearRegression()
    model.fit(X, y)

    future_day = [[df['days'].max() + 30]]
    prediction = model.predict(future_day)

    return round(float(prediction[0]), 2)

# =========================
# INIT
# =========================
if not os.path.exists("expenses.db"):
    create_table()

# =========================
# SIDEBAR
# =========================
st.sidebar.title("💸 Expense Tracker")
menu = ["Dashboard", "Add Expense", "Insights"]
choice = st.sidebar.radio("Navigation", menu)

st.title("💰 Smart Expense Analyzer")

# =========================
# ➕ ADD EXPENSE
# =========================
if choice == "Add Expense":
    st.header("➕ Add Expense")

    col1, col2 = st.columns(2)

    with col1:
        date = st.date_input("Date")
        category = st.selectbox("Category", ["Food", "Travel", "Shopping", "Bills", "Other"])

    with col2:
        amount = st.number_input("Amount", min_value=0)
        description = st.text_input("Description")

    if st.button("Add Expense"):
        add_expense(str(date), category, amount, description)
        st.success("✅ Expense Added!")

# =========================
# 📊 DASHBOARD
# =========================
elif choice == "Dashboard":
    st.header("📊 Dashboard")

    df = get_expenses()

    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])

        total = df["amount"].sum()
        avg = df["amount"].mean()
        count = len(df)

        col1, col2, col3 = st.columns(3)

        col1.metric("💸 Total", f"₹{total}")
        col2.metric("📊 Avg", f"₹{avg:.2f}")
        col3.metric("🧾 Transactions", count)

        # FILTER
        start = st.date_input("Start Date")
        end = st.date_input("End Date")

        df = df[(df['date'] >= str(start)) & (df['date'] <= str(end))]

        col1, col2 = st.columns(2)

        # PIE
        with col1:
            cat = df.groupby("category")["amount"].sum().reset_index()
            fig = px.pie(cat, values="amount", names="category", hole=0.5)
            st.plotly_chart(fig, use_container_width=True)

        # LINE
        with col2:
            df['month'] = df['date'].dt.strftime('%Y-%m')
            monthly = df.groupby('month')['amount'].sum().reset_index()
            monthly = monthly.sort_values("month")

            fig2 = px.line(monthly, x="month", y="amount")
            st.plotly_chart(fig2, use_container_width=True)

        st.dataframe(df)

        st.download_button("Download CSV", df.to_csv(index=False), "expenses.csv")

    else:
        st.info("No data yet!")

# =========================
# 🤖 INSIGHTS
# =========================
elif choice == "Insights":
    st.header("🤖 Smart Insights")

    df = get_expenses()

    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        total = df["amount"].sum()

        # Prediction
        pred = predict_spending(df)
        st.metric("🔮 Next Month Prediction", f"₹{pred}")

        # CATEGORY ANALYSIS
        cat = df.groupby("category")["amount"].sum()
        top_cat = cat.idxmax()
        top_val = cat.max()

        percent = (top_val / total) * 100

        st.info(f"Top Category: {top_cat} (₹{top_val})")

        if percent > 40:
            st.warning(f"⚠ You spend {percent:.1f}% on {top_cat} — reduce it!")
        elif percent > 25:
            st.warning(f"⚠ Moderate high spending on {top_cat}")
        else:
            st.success("✅ Balanced spending")

        # MONTHLY TREND
        df['month'] = df['date'].dt.strftime('%Y-%m')
        monthly = df.groupby('month')['amount'].sum().reset_index()
        monthly = monthly.sort_values("month")

        if len(monthly) > 1:
            last = monthly.iloc[-1]['amount']
            prev = monthly.iloc[-2]['amount']

            change = ((last - prev) / prev) * 100 if prev != 0 else 0

            if change > 20:
                st.warning(f"⚠ Spending increased by {change:.1f}%")
            elif change < -10:
                st.success(f"✅ Reduced spending by {abs(change):.1f}%")
            else:
                st.info("Stable spending")

        # SMART SUGGESTIONS
        st.subheader("🧠 Suggestions")

        if "Food" in cat and (cat["Food"]/total)*100 > 30:
            st.write("🍔 Reduce food delivery spending")

        if "Shopping" in cat and (cat["Shopping"]/total)*100 > 25:
            st.write("🛍 Avoid unnecessary shopping")

        if "Travel" in cat and (cat["Travel"]/total)*100 > 20:
            st.write("✈ Plan travel budget")

    else:
        st.info("Add data to see insights")
