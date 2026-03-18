import streamlit as st
import pandas as pd
import os
import plotly.express as px

from database import create_table
from expense_manager import add_expense, get_expenses
from ml_model import predict_spending

# =========================
# 🎨 PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Smart Expense Analyzer",
    page_icon="💰",
    layout="wide"
)

# =========================
# 🎨 CUSTOM CSS (MODERN DARK UI)
# =========================
st.markdown("""
<style>
body {
    background-color: #0E1117;
    color: white;
}
.stMetric {
    background-color: #1c1f26;
    padding: 15px;
    border-radius: 10px;
}
.stButton>button {
    background-color: #4CAF50;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 🗄 DATABASE INIT
# =========================
if not os.path.exists("expenses.db"):
    create_table()

# =========================
# 📌 SIDEBAR
# =========================
st.sidebar.title("💸 Expense Tracker")
st.sidebar.markdown("Track • Analyze • Save")

menu = ["Dashboard", "Add Expense", "Insights"]
choice = st.sidebar.radio("Navigation", menu)

st.title("💰 Smart Expense Analyzer")

# =========================
# ➕ ADD EXPENSE
# =========================
if choice == "Add Expense":
    st.subheader("➕ Add New Expense")

    col1, col2 = st.columns(2)

    with col1:
        date = st.date_input("Date")
        category = st.selectbox("Category", ["Food", "Travel", "Shopping", "Bills", "Other"])

    with col2:
        amount = st.number_input("Amount", min_value=0)
        description = st.text_input("Description")

    if st.button("Add Expense"):
        add_expense(str(date), category, amount, description)
        st.success("✅ Expense Added Successfully!")

# =========================
# 📊 DASHBOARD
# =========================
elif choice == "Dashboard":
    st.subheader("📊 Financial Overview")

    df = get_expenses()

    if df is not None and not df.empty:
        df['date'] = pd.to_datetime(df['date'])

        # 💳 Cards
        total = df["amount"].sum()
        avg = df["amount"].mean()
        count = len(df)

        col1, col2, col3 = st.columns(3)

        col1.markdown(f"""
        <div style="background:#1c1f26;padding:20px;border-radius:10px">
        <h4>💸 Total</h4>
        <h2>₹{total}</h2>
        </div>
        """, unsafe_allow_html=True)

        col2.markdown(f"""
        <div style="background:#1c1f26;padding:20px;border-radius:10px">
        <h4>📊 Average</h4>
        <h2>₹{avg:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

        col3.markdown(f"""
        <div style="background:#1c1f26;padding:20px;border-radius:10px">
        <h4>🧾 Transactions</h4>
        <h2>{count}</h2>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # 📅 Filters
        col1, col2 = st.columns(2)
        with col1:
            start = st.date_input("Start Date")
        with col2:
            end = st.date_input("End Date")

        df = df[(df['date'] >= str(start)) & (df['date'] <= str(end))]

        # 📊 Charts
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📂 Category Split")
            category_data = df.groupby("category")["amount"].sum().reset_index()

            fig = px.pie(
                category_data,
                values="amount",
                names="category",
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("📈 Monthly Trend")
            df['month'] = df['date'].dt.to_period('M')
            monthly = df.groupby('month')['amount'].sum().reset_index()

            fig2 = px.line(monthly, x="month", y="amount")
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")

        # 📋 Transactions Table
        st.subheader("📋 Transactions")

        def get_icon(cat):
            icons = {
                "Food": "🍔",
                "Travel": "✈",
                "Shopping": "🛍",
                "Bills": "📄",
                "Other": "📦"
            }
            return icons.get(cat, "📦")

        df["Category"] = df["category"].apply(lambda x: f"{get_icon(x)} {x}")

        st.dataframe(df[["date", "Category", "amount", "description"]])

        # ⬇ Download
        st.download_button(
            "⬇ Download Report",
            df.to_csv(index=False),
            "expenses.csv"
        )

    else:
        st.info("No data yet. Add some expenses!")

# =========================
# 🤖 INSIGHTS
# =========================
elif choice == "Insights":
    st.subheader("🤖 Smart Insights")

    df = get_expenses()

    if df is not None and not df.empty:
        total = df["amount"].sum()

        prediction = predict_spending(df)
        st.metric("🔮 Next Month Prediction", f"₹{prediction}")

        st.markdown("---")

        category_data = df.groupby("category")["amount"].sum()
        top_category = category_data.idxmax()

        st.info(f"💡 You spend most on **{top_category}**")

        if category_data.max() > (total * 0.4):
            st.warning("⚠ Try reducing spending in this category!")

        st.success("✅ Keep tracking your expenses regularly!")

    else:
        st.info("Add data to see insights")
