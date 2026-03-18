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
# 🎨 PREMIUM CSS
# =========================
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
}

/* Glass Card */
.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
    box-shadow: 0px 4px 20px rgba(0,0,0,0.3);
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #22c55e, #4ade80);
    color: black;
    border-radius: 10px;
    font-weight: bold;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #020617;
}

/* Titles */
h1, h2, h3 {
    color: #e2e8f0;
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
st.sidebar.markdown("## 💸 Expense Tracker")
st.sidebar.markdown("### Track • Analyze • Save")

menu = ["Dashboard", "Add Expense", "Insights"]
choice = st.sidebar.radio("Navigation", menu)

st.markdown("# 💰 Smart Expense Analyzer")

# =========================
# ➕ ADD EXPENSE
# =========================
if choice == "Add Expense":
    st.markdown("## ➕ Add New Expense")

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
    st.markdown("## 📊 Financial Overview")

    df = get_expenses()

    if df is not None and not df.empty:
        df['date'] = pd.to_datetime(df['date'])

        total = df["amount"].sum()
        avg = df["amount"].mean()
        count = len(df)

        # 💳 CARDS
        col1, col2, col3 = st.columns(3)

        col1.markdown(f"""
        <div class="card">
        <h4>💸 Total Spending</h4>
        <h2>₹{total}</h2>
        </div>
        """, unsafe_allow_html=True)

        col2.markdown(f"""
        <div class="card">
        <h4>📊 Average</h4>
        <h2>₹{avg:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

        col3.markdown(f"""
        <div class="card">
        <h4>🧾 Transactions</h4>
        <h2>{count}</h2>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # 📅 FILTERS
        col1, col2 = st.columns(2)
        with col1:
            start = st.date_input("Start Date")
        with col2:
            end = st.date_input("End Date")

        df = df[(df['date'] >= str(start)) & (df['date'] <= str(end))]

        # 📊 CHARTS
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📂 Category Split")
            category_data = df.groupby("category")["amount"].sum().reset_index()

            fig = px.pie(category_data, values="amount", names="category", hole=0.5)
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### 📈 Monthly Trend")
            df['month'] = df['date'].dt.to_period('M')
            monthly = df.groupby('month')['amount'].sum().reset_index()

            fig2 = px.line(monthly, x="month", y="amount")
            fig2.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")

        # 📋 TABLE
        st.markdown("### 📋 Transactions")

        def icon(cat):
            return {
                "Food": "🍔",
                "Travel": "✈",
                "Shopping": "🛍",
                "Bills": "📄",
                "Other": "📦"
            }.get(cat, "📦")

        df["Category"] = df["category"].apply(lambda x: f"{icon(x)} {x}")

        st.dataframe(df[["date", "Category", "amount", "description"]])

        st.download_button("⬇ Download Report", df.to_csv(index=False), "expenses.csv")

    else:
        st.info("No data yet. Add some expenses!")

# =========================
# 🤖 INSIGHTS
# =========================
elif choice == "Insights":
    st.markdown("## 🤖 Smart Insights")

    df = get_expenses()

    if df is not None and not df.empty:
        total = df["amount"].sum()

        prediction = predict_spending(df)
        st.metric("🔮 Next Month Prediction", f"₹{prediction}")

        st.markdown("---")

        category_data = df.groupby("category")["amount"].sum()
        top_category = category_data.idxmax()

        st.info(f"💡 You spend the most on **{top_category}**")

        if category_data.max() > (total * 0.4):
            st.warning("⚠ High spending detected — consider reducing this category.")

        st.success("✅ You're actively tracking finances — great job!")

    else:
        st.info("Add data to see insights")
