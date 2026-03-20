import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64

# =========================
# 🎨 UI & CONFIG
# =========================
st.set_page_config(page_title="NexFin Pro | Intelligence", page_icon="💎", layout="wide")

def apply_custom_design():
    st.markdown("""
    <style>
        .main { background-color: #0f172a; }
        .stMetric { background: rgba(30, 41, 59, 0.7); padding: 15px; border-radius: 12px; border: 1px solid #334155; }
        .footer { position: fixed; bottom: 10px; right: 10px; color: #94a3b8; font-size: 12px; }
        .status-chip { padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

apply_custom_design()

# =========================
# 🗄 DATABASE LAYER
# =========================
DB_NAME = "nexfin_pro.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS expenses
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         date TEXT, category TEXT, amount REAL, desc TEXT)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS budgets
                        (category TEXT PRIMARY KEY, limit_amt REAL)""")

def db_execute(query, params=(), is_select=True):
    with sqlite3.connect(DB_NAME) as conn:
        if is_select: return pd.read_sql(query, conn, params=params)
        conn.execute(query, params)
        conn.commit()

init_db()

# =========================
# 🛠 UTILITIES
# =========================
def get_csv_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="expenses_{datetime.now().strftime("%Y%m%d")}.csv" style="text-decoration:none;"><button style="background-color:#22c55e; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer;">📥 Export to CSV</button></a>'

# =========================
# 📱 NAVIGATION
# =========================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135706.png", width=80)
    st.title("NexFin Pro")
    menu = st.radio("Menu", ["📊 Analysis", "🎯 Budgets", "➕ Transactions", "⚙️ Settings"])
    st.markdown("---")
    st.caption("v2.4.0-Stable")

# =========================
# 📊 ANALYSIS PAGE
# =========================
if menu == "📊 Analysis":
    st.title("Financial Intelligence")
    df = db_execute("SELECT * FROM expenses ORDER BY date DESC")
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        
        # 1. KPIs
        c1, c2, c3, c4 = st.columns(4)
        total = df['amount'].sum()
        this_month = df[df['date'].dt.month == datetime.now().month]['amount'].sum()
        
        c1.metric("Lifetime Outflow", f"₹{total:,.0f}")
        c2.metric("Monthly Spending", f"₹{this_month:,.0f}", delta=f"{this_month/total*100:.1f}% of total")
        c3.metric("Avg Transaction", f"₹{df['amount'].mean():,.0f}")
        c4.metric("Active Categories", df['category'].nunique())

        # 2. Visuals
        st.markdown("### 📈 Trends & Distribution")
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            # Time Series with Range Selector
            trend_df = df.groupby('date')['amount'].sum().reset_index()
            fig_line = px.line(trend_df, x='date', y='amount', title="Daily Spend Flow")
            fig_line.update_xaxes(rangeslider_visible=True)
            st.plotly_chart(fig_line, use_container_width=True)
            
        with col_right:
            # Category Breakdown
            fig_sun = px.sunburst(df, path=['category', 'desc'], values='amount', title="Category Depth")
            st.plotly_chart(fig_sun, use_container_width=True)

        # 3. Data Table & Export
        st.markdown("### 📝 Detailed Logs")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown(get_csv_download_link(df), unsafe_allow_html=True)
    else:
        st.info("No records found. Visit the Transactions tab to get started.")

# =========================
# 🎯 BUDGETS PAGE
# =========================
elif menu == "🎯 Budgets":
    st.title("Budget Control Center")
    
    # Set Budget
    with st.expander("🛠 Define Category Budgets"):
        bc1, bc2 = st.columns(2)
        cat = bc1.selectbox("Choose Category", ["🏠 Rent", "🍱 Food", "🚗 Transport", "🎬 Entertainment", "🛍 Shopping", "💡 Bills"])
        limit = bc2.number_input("Monthly Limit (₹)", min_value=0)
        if st.button("Set Budget"):
            db_execute("INSERT OR REPLACE INTO budgets (category, limit_amt) VALUES (?,?)", (cat, limit), False)
            st.success("Budget Updated!")

    # Analysis
    st.markdown("### 📊 Budget vs. Actual (This Month)")
    budgets = db_execute("SELECT * FROM budgets")
    expenses = db_execute("SELECT category, SUM(amount) as spent FROM expenses WHERE strftime('%m', date) = strftime('%m', 'now') GROUP BY category")
    
    if not budgets.empty:
        comparison = pd.merge(budgets, expenses, on="category", how="left").fillna(0)
        comparison['remaining'] = comparison['limit_amt'] - comparison['spent']
        
        for index, row in comparison.iterrows():
            progress = min(row['spent'] / row['limit_amt'], 1.0) if row['limit_amt'] > 0 else 0
            color = "green" if progress < 0.8 else "orange" if progress < 1.0 else "red"
            
            st.write(f"**{row['category']}** ({row['spent']:,.0f} / {row['limit_amt']:,.0f})")
            st.progress(progress)
            if row['remaining'] < 0:
                st.error(f"⚠️ Over budget by ₹{abs(row['remaining']):,.0f}!")
    else:
        st.warning("No budgets set yet.")

# =========================
# ➕ TRANSACTIONS PAGE
# =========================
elif menu == "➕ Transactions":
    st.title("Transaction Manager")
    
    t1, t2 = st.tabs(["Add New", "Manage Existing"])
    
    with t1:
        with st.form("new_txn", clear_on_submit=True):
            tc1, tc2, tc3 = st.columns(3)
            date = tc1.date_input("Date")
            cat = tc2.selectbox("Category", ["🏠 Rent", "🍱 Food", "🚗 Transport", "🎬 Entertainment", "🛍 Shopping", "💡 Bills", "💊 Health", "✨ Other"])
            amt = tc3.number_input("Amount", min_value=0.0)
            desc = st.text_input("Description (Keep it short)")
            if st.form_submit_button("Save Transaction"):
                db_execute("INSERT INTO expenses (date, category, amount, desc) VALUES (?,?,?,?)", (str(date), cat, amt, desc), False)
                st.toast("Transaction logged!", icon="✅")
    
    with t2:
        df_manage = db_execute("SELECT * FROM expenses ORDER BY id DESC")
        if not df_manage.empty:
            del_id = st.number_input("Enter ID to Delete", step=1, min_value=int(df_manage['id'].min()))
            if st.button("🗑 Delete Record"):
                db_execute("DELETE FROM expenses WHERE id = ?", (del_id,), False)
                st.rerun()
            st.dataframe(df_manage, use_container_width=True)

# =========================
# ⚙️ SETTINGS
# =========================
elif menu == "⚙️ Settings":
    st.title("System Settings")
    if st.button("🧨 Factory Reset (Clear All Data)"):
        db_execute("DELETE FROM expenses", is_select=False)
        db_execute("DELETE FROM budgets", is_select=False)
        st.warning("All data wiped.")
