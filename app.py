import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64
import calendar
import json

# =========================
# 🎨 PAGE CONFIG
# =========================
st.set_page_config(
    page_title="NexFin Pro",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# 🎨 DESIGN SYSTEM
# =========================
def apply_design():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --bg-deep:     #080c14;
        --bg-surface:  #0d1420;
        --bg-card:     #111827;
        --bg-hover:    #1a2336;
        --border:      #1e2d45;
        --border-glow: #2563eb44;
        --accent:      #3b82f6;
        --accent-2:    #06b6d4;
        --accent-warm: #f59e0b;
        --success:     #10b981;
        --danger:      #ef4444;
        --warning:     #f59e0b;
        --text-1:      #f1f5f9;
        --text-2:      #94a3b8;
        --text-3:      #475569;
    }

    html, body, [class*="css"] {
        font-family: 'Syne', sans-serif;
        background-color: var(--bg-deep);
        color: var(--text-1);
    }

    /* SCROLLBAR */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: var(--bg-surface); }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }

    /* HIDE STREAMLIT CHROME */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 1.5rem 2rem 2rem; max-width: 1400px; }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background: var(--bg-surface);
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] .block-container { padding: 1.5rem 1rem; }

    /* RADIO BUTTONS (nav) */
    div[data-testid="stRadio"] > label { display: none; }
    div[data-testid="stRadio"] > div {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    div[data-testid="stRadio"] label {
        background: transparent;
        border: 1px solid transparent;
        border-radius: 10px;
        padding: 10px 14px;
        cursor: pointer;
        transition: all 0.2s;
        color: var(--text-2);
        font-weight: 500;
        font-size: 14px;
    }
    div[data-testid="stRadio"] label:hover {
        background: var(--bg-hover);
        color: var(--text-1);
        border-color: var(--border);
    }
    div[data-testid="stRadio"] [data-testid="stMarkdownContainer"] { display: flex; align-items: center; gap: 10px; }

    /* METRICS */
    [data-testid="stMetric"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 18px 20px !important;
        transition: border-color 0.2s;
    }
    [data-testid="stMetric"]:hover { border-color: var(--accent); }
    [data-testid="stMetric"] label { color: var(--text-2) !important; font-size: 12px !important; text-transform: uppercase; letter-spacing: 1px; }
    [data-testid="stMetricValue"] { color: var(--text-1) !important; font-size: 1.8rem !important; font-weight: 700 !important; }
    [data-testid="stMetricDelta"] { font-size: 12px !important; }

    /* DATAFRAME */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
    }

    /* FORMS */
    [data-testid="stForm"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 24px;
    }

    /* BUTTONS */
    .stButton > button {
        background: var(--accent) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.2s !important;
        letter-spacing: 0.3px;
    }
    .stButton > button:hover {
        background: #2563eb !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 20px #3b82f644;
    }

    /* INPUTS */
    .stSelectbox > div > div, .stNumberInput > div > div, .stTextInput > div > div {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text-1) !important;
    }

    /* EXPANDER */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        color: var(--text-1) !important;
    }

    /* TABS */
    [data-testid="stTabs"] [role="tab"] {
        color: var(--text-2);
        font-weight: 600;
        font-size: 14px;
        padding: 8px 20px;
    }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        color: var(--accent) !important;
        border-bottom: 2px solid var(--accent) !important;
    }

    /* ALERTS */
    .stAlert { border-radius: 12px; border: none; }

    /* PROGRESS */
    .stProgress > div > div > div { border-radius: 100px; }

    /* CUSTOM CARDS */
    .kpi-hero {
        background: linear-gradient(135deg, #1e3a5f 0%, #0f2744 100%);
        border: 1px solid var(--accent);
        border-radius: 20px;
        padding: 28px 32px;
        position: relative;
        overflow: hidden;
    }
    .kpi-hero::before {
        content: '';
        position: absolute;
        top: -40px; right: -40px;
        width: 180px; height: 180px;
        background: radial-gradient(circle, #3b82f622 0%, transparent 70%);
        border-radius: 50%;
    }
    .kpi-hero h2 { margin: 0; font-size: 2.4rem; font-weight: 800; color: white; }
    .kpi-hero p  { margin: 4px 0 0; color: #93c5fd; font-size: 13px; text-transform: uppercase; letter-spacing: 1.5px; }

    .budget-bar-wrap {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 12px;
        transition: border-color 0.2s;
    }
    .budget-bar-wrap:hover { border-color: var(--accent); }

    .tag {
        display: inline-block;
        background: #1e3a5f;
        color: #93c5fd;
        border: 1px solid #2563eb44;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        padding: 2px 10px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .tag-warn { background: #3f2a00; color: #fbbf24; border-color: #f59e0b44; }
    .tag-danger { background: #3f0d0d; color: #f87171; border-color: #ef444444; }
    .tag-success { background: #052e16; color: #34d399; border-color: #10b98144; }

    .section-header {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--text-3);
        margin: 24px 0 14px;
    }

    .page-title {
        font-size: 2rem;
        font-weight: 800;
        color: var(--text-1);
        margin-bottom: 2px;
        line-height: 1.1;
    }
    .page-subtitle {
        font-size: 13px;
        color: var(--text-2);
        margin-bottom: 24px;
    }

    .insight-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-left: 3px solid var(--accent);
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 10px;
        font-size: 13px;
    }

    .mono { font-family: 'JetBrains Mono', monospace; }
    </style>
    """, unsafe_allow_html=True)

apply_design()

# =========================
# 🗄 DATABASE
# =========================
DB_NAME = "/tmp/nexfin_pro.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            desc TEXT,
            payment_method TEXT DEFAULT 'Cash',
            is_recurring INTEGER DEFAULT 0
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS budgets (
            category TEXT PRIMARY KEY,
            limit_amt REAL NOT NULL
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS savings_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            target REAL NOT NULL,
            saved REAL DEFAULT 0,
            deadline TEXT,
            icon TEXT DEFAULT '🎯'
        )""")

def db_select(query, params=()):
    with sqlite3.connect(DB_NAME) as conn:
        return pd.read_sql(query, conn, params=params)

def db_write(query, params=()):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(query, params)
        conn.commit()

init_db()

# =========================
# 🛠 UTILITIES
# =========================
CATEGORIES = ["🏠 Rent", "🍱 Food", "🚗 Transport", "🎬 Entertainment",
              "🛍 Shopping", "💡 Bills", "💊 Health", "📚 Education",
              "✈️ Travel", "💪 Fitness", "🎁 Gifts", "✨ Other"]
PAYMENT_METHODS = ["💳 Card", "💵 Cash", "📱 UPI", "🏦 Net Banking", "📲 Wallet"]
ICONS = ["🎯","🏠","🚗","💻","📱","✈️","💍","🎓","🏖️","💰"]

def export_csv(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="nexfin_export_{datetime.now().strftime("%Y%m%d_%H%M")}.csv"><button style="background:#3b82f6;color:white;border:none;padding:10px 22px;border-radius:10px;cursor:pointer;font-family:Syne,sans-serif;font-weight:600;font-size:13px;">📥 Export CSV</button></a>'

def pct_change(current, previous):
    if previous == 0: return 0
    return ((current - previous) / previous) * 100

def get_month_range(offset=0):
    now = datetime.now()
    month = (now.month - offset - 1) % 12 + 1
    year = now.year - ((now.month - offset - 1) // 12)
    first = datetime(year, month, 1)
    last = datetime(year, month, calendar.monthrange(year, month)[1])
    return first.strftime('%Y-%m-%d'), last.strftime('%Y-%m-%d')

# =========================
# 🎛 SIDEBAR
# =========================
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 8px 0 20px;'>
        <div style='font-size:32px;'>💎</div>
        <div style='font-size:20px; font-weight:800; color:#f1f5f9; letter-spacing:-0.5px;'>NexFin Pro</div>
        <div style='font-size:11px; color:#475569; letter-spacing:2px; text-transform:uppercase; margin-top:2px;'>Financial Intelligence</div>
    </div>
    """, unsafe_allow_html=True)

    menu = st.radio("Navigation", [
        "📊 Dashboard",
        "📈 Analytics",
        "🎯 Budgets",
        "🏦 Savings Goals",
        "➕ Add Transaction",
        "📋 All Transactions",
        "⚙️ Settings"
    ])

    st.markdown("<hr style='border-color:#1e2d45; margin: 16px 0;'>", unsafe_allow_html=True)

    # Quick Stats in sidebar
    df_all = db_select("SELECT * FROM expenses")
    if not df_all.empty:
        total_spend = df_all['amount'].sum()
        st.markdown(f"""
        <div style='font-size:11px; color:#475569; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:10px;'>QUICK STATS</div>
        <div style='display:flex; flex-direction:column; gap:6px;'>
            <div style='display:flex; justify-content:space-between; font-size:13px; color:#94a3b8;'>
                <span>Total Logged</span>
                <span style='color:#f1f5f9; font-weight:600;' class='mono'>₹{total_spend:,.0f}</span>
            </div>
            <div style='display:flex; justify-content:space-between; font-size:13px; color:#94a3b8;'>
                <span>Transactions</span>
                <span style='color:#f1f5f9; font-weight:600;'>{len(df_all)}</span>
            </div>
            <div style='display:flex; justify-content:space-between; font-size:13px; color:#94a3b8;'>
                <span>Categories</span>
                <span style='color:#f1f5f9; font-weight:600;'>{df_all['category'].nunique()}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#1e2d45; margin: 16px 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:11px; color:#334155; text-align:center;'>v3.0.0 · NexFin Pro</div>", unsafe_allow_html=True)

# =========================
# 🎨 PLOTLY THEME
# =========================
CHART_THEME = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Syne', color='#94a3b8', size=12),
    colorway=['#3b82f6','#06b6d4','#10b981','#f59e0b','#ef4444','#8b5cf6','#ec4899'],
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(gridcolor='#1e2d45', linecolor='#1e2d45', tickfont=dict(size=11)),
    yaxis=dict(gridcolor='#1e2d45', linecolor='#1e2d45', tickfont=dict(size=11))
)

# =========================
# 📊 DASHBOARD PAGE
# =========================
if menu == "📊 Dashboard":
    st.markdown('<div class="page-title">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Your financial overview at a glance</div>', unsafe_allow_html=True)

    df = db_select("SELECT * FROM expenses ORDER BY date DESC")

    if df.empty:
        st.info("🚀 No transactions yet. Head to **Add Transaction** to get started!")
        st.stop()

    df['date'] = pd.to_datetime(df['date'])
    start_this, end_this = get_month_range(0)
    start_prev, end_prev = get_month_range(1)

    this_month_df = df[(df['date'] >= start_this) & (df['date'] <= end_this)]
    prev_month_df = df[(df['date'] >= start_prev) & (df['date'] <= end_prev)]

    this_total   = this_month_df['amount'].sum()
    prev_total   = prev_month_df['amount'].sum()
    change       = pct_change(this_total, prev_total)
    avg_daily    = this_month_df.groupby('date')['amount'].sum().mean() if not this_month_df.empty else 0
    top_cat      = this_month_df.groupby('category')['amount'].sum().idxmax() if not this_month_df.empty else "—"

    # Hero KPI
    col_hero, col_r = st.columns([3, 1])
    with col_hero:
        st.markdown(f"""
        <div class="kpi-hero">
            <p>THIS MONTH'S SPENDING</p>
            <h2>₹{this_total:,.0f}</h2>
            <div style='margin-top:12px; display:flex; gap:20px;'>
                <div>
                    <div style='font-size:11px; color:#93c5fd; text-transform:uppercase; letter-spacing:1px;'>vs Last Month</div>
                    <div style='font-size:18px; font-weight:700; color:{"#ef4444" if change>0 else "#10b981"};'>
                        {"▲" if change>0 else "▼"} {abs(change):.1f}%
                    </div>
                </div>
                <div>
                    <div style='font-size:11px; color:#93c5fd; text-transform:uppercase; letter-spacing:1px;'>Daily Avg</div>
                    <div style='font-size:18px; font-weight:700; color:#f1f5f9;'>₹{avg_daily:,.0f}</div>
                </div>
                <div>
                    <div style='font-size:11px; color:#93c5fd; text-transform:uppercase; letter-spacing:1px;'>Top Category</div>
                    <div style='font-size:16px; font-weight:700; color:#f1f5f9;'>{top_cat}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Other KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Lifetime", f"₹{df['amount'].sum():,.0f}", f"{len(df)} transactions")
    c2.metric("Avg Transaction", f"₹{df['amount'].mean():,.0f}")
    c3.metric("Largest Spend", f"₹{df['amount'].max():,.0f}", df.loc[df['amount'].idxmax(), 'category'])
    c4.metric("Active Categories", df['category'].nunique(), "categories tracked")

    # Charts Row
    st.markdown('<div class="section-header">SPENDING TRENDS</div>', unsafe_allow_html=True)
    cl, cr = st.columns([2, 1])

    with cl:
        trend = df.groupby(df['date'].dt.date)['amount'].sum().reset_index()
        trend.columns = ['date', 'amount']
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=trend['date'], y=trend['amount'],
            mode='lines', fill='tozeroy',
            line=dict(color='#3b82f6', width=2),
            fillcolor='rgba(59,130,246,0.1)',
            name='Daily Spend'
        ))
        fig.update_layout(title='Daily Spending Flow', **CHART_THEME)
        st.plotly_chart(fig, use_container_width=True)

    with cr:
        cat_df = df.groupby('category')['amount'].sum().reset_index()
        fig2 = px.pie(cat_df, values='amount', names='category',
                      title='Category Split', hole=0.55,
                      color_discrete_sequence=px.colors.qualitative.Set3)
        fig2.update_layout(**CHART_THEME)
        fig2.update_traces(textfont_size=11, textposition='outside')
        st.plotly_chart(fig2, use_container_width=True)

    # Monthly Comparison Bar
    st.markdown('<div class="section-header">MONTHLY COMPARISON</div>', unsafe_allow_html=True)
    monthly = df.groupby(df['date'].dt.to_period('M'))['amount'].sum().reset_index()
    monthly['date'] = monthly['date'].astype(str)
    fig3 = px.bar(monthly, x='date', y='amount', title='Month-over-Month Spending',
                  color='amount', color_continuous_scale='Blues')
    fig3.update_layout(**CHART_THEME, showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

    # Recent Transactions
    st.markdown('<div class="section-header">RECENT TRANSACTIONS</div>', unsafe_allow_html=True)
    recent = df.head(8)[['date','category','amount','desc','payment_method']].copy()
    recent['date'] = recent['date'].dt.strftime('%d %b %Y')
    recent['amount'] = recent['amount'].apply(lambda x: f"₹{x:,.0f}")
    st.dataframe(recent, use_container_width=True, hide_index=True)

# =========================
# 📈 ANALYTICS PAGE
# =========================
elif menu == "📈 Analytics":
    st.markdown('<div class="page-title">Deep Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Dig into spending patterns & insights</div>', unsafe_allow_html=True)

    df = db_select("SELECT * FROM expenses")
    if df.empty:
        st.info("No data yet.")
        st.stop()

    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M').astype(str)
    df['dow']   = df['date'].dt.day_name()
    df['week']  = df['date'].dt.isocalendar().week.astype(int)
    df['hour']  = 12  # default since time not tracked

    tab1, tab2, tab3 = st.tabs(["📅 Time Analysis", "🗂 Category Breakdown", "🔍 Insights"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            # Heatmap by Day of Week
            dow_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
            dow_spend = df.groupby('dow')['amount'].sum().reindex(dow_order).reset_index()
            fig = px.bar(dow_spend, x='dow', y='amount', title='Spending by Day of Week',
                         color='amount', color_continuous_scale='Blues')
            fig.update_layout(**CHART_THEME, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            # Monthly trend per category
            mc = df.groupby(['month','category'])['amount'].sum().reset_index()
            fig2 = px.line(mc, x='month', y='amount', color='category',
                           title='Category Trends Over Time', markers=True)
            fig2.update_layout(**CHART_THEME)
            st.plotly_chart(fig2, use_container_width=True)

        # Weekly rolling average
        daily = df.groupby('date')['amount'].sum().reset_index()
        daily = daily.sort_values('date')
        daily['7d_avg'] = daily['amount'].rolling(7, min_periods=1).mean()
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=daily['date'], y=daily['amount'], name='Daily', marker_color='#1e3a5f'))
        fig3.add_trace(go.Scatter(x=daily['date'], y=daily['7d_avg'], name='7-Day Avg',
                                  line=dict(color='#3b82f6', width=2)))
        fig3.update_layout(title='Daily Spend + 7-Day Rolling Average', **CHART_THEME)
        st.plotly_chart(fig3, use_container_width=True)

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            cat_total = df.groupby('category')['amount'].sum().sort_values(ascending=True).reset_index()
            fig = px.bar(cat_total, x='amount', y='category', orientation='h',
                         title='Total by Category', color='amount', color_continuous_scale='Blues')
            fig.update_layout(**CHART_THEME, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            fig2 = px.sunburst(df, path=['category', 'desc'], values='amount',
                               title='Category → Item Breakdown',
                               color_discrete_sequence=px.colors.qualitative.Set3)
            fig2.update_layout(**CHART_THEME)
            st.plotly_chart(fig2, use_container_width=True)

        # Payment method breakdown
        if 'payment_method' in df.columns:
            pm = df.groupby('payment_method')['amount'].sum().reset_index()
            fig3 = px.pie(pm, values='amount', names='payment_method',
                          title='Spending by Payment Method', hole=0.4)
            fig3.update_layout(**CHART_THEME)
            st.plotly_chart(fig3, use_container_width=True)

    with tab3:
        st.markdown('<div class="section-header">AI-POWERED INSIGHTS</div>', unsafe_allow_html=True)

        top_cat    = df.groupby('category')['amount'].sum().idxmax()
        top_amt    = df.groupby('category')['amount'].sum().max()
        avg_txn    = df['amount'].mean()
        biggest    = df.loc[df['amount'].idxmax()]
        most_freq  = df['category'].value_counts().idxmax()
        monthly_avg = df.groupby(df['date'].dt.to_period('M'))['amount'].sum().mean()

        insights = [
            (f"💸 Your biggest spend category is <b>{top_cat}</b> at ₹{top_amt:,.0f} — consider reviewing it.", "blue"),
            (f"📊 Your average transaction is <b>₹{avg_txn:,.0f}</b>. Transactions above this are above your baseline.", "neutral"),
            (f"🔝 Biggest single transaction: <b>₹{biggest['amount']:,.0f}</b> on {biggest['desc']} ({biggest['category']}).", "neutral"),
            (f"🔁 You transact most in <b>{most_freq}</b> — possibly subscription or daily expenses.", "blue"),
            (f"📅 Monthly average spend: <b>₹{monthly_avg:,.0f}</b>. Use this for budget planning.", "neutral"),
        ]

        for text, _ in insights:
            st.markdown(f'<div class="insight-card">{text}</div>', unsafe_allow_html=True)

# =========================
# 🎯 BUDGETS PAGE
# =========================
elif menu == "🎯 Budgets":
    st.markdown('<div class="page-title">Budget Control</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Set limits. Track actuals. Stay in control.</div>', unsafe_allow_html=True)

    with st.expander("➕ Add / Update Budget"):
        bc1, bc2, bc3 = st.columns([2,2,1])
        cat   = bc1.selectbox("Category", CATEGORIES)
        limit = bc2.number_input("Monthly Limit (₹)", min_value=0.0, step=500.0)
        bc3.markdown("<br>", unsafe_allow_html=True)
        if bc3.button("Save"):
            db_write("INSERT OR REPLACE INTO budgets VALUES (?,?)", (cat, limit))
            st.success(f"Budget set for {cat}: ₹{limit:,.0f}")

    st.markdown('<div class="section-header">THIS MONTH\'S BUDGET STATUS</div>', unsafe_allow_html=True)
    budgets  = db_select("SELECT * FROM budgets")
    start, end = get_month_range(0)
    expenses = db_select(f"""
        SELECT category, SUM(amount) as spent FROM expenses
        WHERE date BETWEEN '{start}' AND '{end}'
        GROUP BY category
    """)

    if budgets.empty:
        st.warning("No budgets set yet. Add your first budget above.")
    else:
        merged = pd.merge(budgets, expenses, on='category', how='left').fillna(0)
        merged['remaining'] = merged['limit_amt'] - merged['spent']
        merged['pct']       = (merged['spent'] / merged['limit_amt'].replace(0, 1)) * 100

        for _, row in merged.iterrows():
            pct = min(row['pct'], 100)
            color = "#10b981" if pct < 70 else "#f59e0b" if pct < 90 else "#ef4444"
            tag = "ON TRACK" if pct < 70 else "WARNING" if pct < 90 else "OVER BUDGET"
            tag_class = "tag-success" if pct < 70 else "tag-warn" if pct < 90 else "tag-danger"

            st.markdown(f"""
            <div class="budget-bar-wrap">
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;'>
                    <div style='font-weight:700; font-size:15px;'>{row['category']}</div>
                    <div style='display:flex; gap:10px; align-items:center;'>
                        <span class='mono' style='font-size:13px; color:#94a3b8;'>₹{row['spent']:,.0f} / ₹{row['limit_amt']:,.0f}</span>
                        <span class='tag {tag_class}'>{tag}</span>
                    </div>
                </div>
                <div style='background:#1e2d45; border-radius:100px; height:8px; overflow:hidden;'>
                    <div style='background:{color}; width:{pct}%; height:100%; border-radius:100px; transition:width 0.5s;'></div>
                </div>
                <div style='display:flex; justify-content:space-between; margin-top:6px;'>
                    <span style='font-size:12px; color:#475569;'>{pct:.1f}% used</span>
                    <span style='font-size:12px; color:{"#ef4444" if row["remaining"]<0 else "#10b981"};'>
                        {"Over by" if row["remaining"]<0 else "Remaining"}: ₹{abs(row["remaining"]):,.0f}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Summary chart
        st.markdown('<div class="section-header">BUDGET vs ACTUAL</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Budget', x=merged['category'], y=merged['limit_amt'],
                             marker_color='#1e3a5f'))
        fig.add_trace(go.Bar(name='Spent',  x=merged['category'], y=merged['spent'],
                             marker_color='#3b82f6'))
        fig.update_layout(barmode='group', title='Budget vs Actual This Month', **CHART_THEME)
        st.plotly_chart(fig, use_container_width=True)

# =========================
# 🏦 SAVINGS GOALS
# =========================
elif menu == "🏦 Savings Goals":
    st.markdown('<div class="page-title">Savings Goals</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Track progress toward your financial milestones</div>', unsafe_allow_html=True)

    with st.expander("➕ New Savings Goal"):
        g1, g2, g3, g4 = st.columns([2,1,1,1])
        gname    = g1.text_input("Goal Name", placeholder="e.g. Emergency Fund")
        gtarget  = g2.number_input("Target (₹)", min_value=100.0, step=1000.0)
        gsaved   = g3.number_input("Already Saved (₹)", min_value=0.0, step=100.0)
        gdeadline = g4.date_input("Target Date")
        gicon    = st.selectbox("Icon", ICONS)
        if st.button("Create Goal"):
            db_write("INSERT INTO savings_goals (name, target, saved, deadline, icon) VALUES (?,?,?,?,?)",
                     (gname, gtarget, gsaved, str(gdeadline), gicon))
            st.success(f"Goal '{gname}' created!")
            st.rerun()

    goals = db_select("SELECT * FROM savings_goals")

    if goals.empty:
        st.info("No savings goals yet. Create your first one above!")
    else:
        for i, row in goals.iterrows():
            pct  = min((row['saved'] / row['target']) * 100, 100) if row['target'] > 0 else 0
            days_left = (pd.to_datetime(row['deadline']) - datetime.now()).days if row['deadline'] else None

            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.markdown(f"""
                <div style='background:#111827; border:1px solid #1e2d45; border-radius:14px; padding:18px 20px;'>
                    <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;'>
                        <div style='display:flex; align-items:center; gap:12px;'>
                            <span style='font-size:24px;'>{row['icon']}</span>
                            <div>
                                <div style='font-weight:700; font-size:16px;'>{row['name']}</div>
                                <div style='font-size:12px; color:#475569;'>
                                    {f"Due {row['deadline']}" if row['deadline'] else "No deadline"} 
                                    {f"· {days_left} days left" if days_left and days_left >= 0 else ""}
                                </div>
                            </div>
                        </div>
                        <div style='text-align:right;'>
                            <div style='font-size:22px; font-weight:800; color:#f1f5f9;'>{pct:.0f}%</div>
                            <div style='font-size:12px; color:#94a3b8;'>₹{row["saved"]:,.0f} / ₹{row["target"]:,.0f}</div>
                        </div>
                    </div>
                    <div style='background:#1e2d45; border-radius:100px; height:10px; overflow:hidden;'>
                        <div style='background:{"#10b981" if pct >= 100 else "#3b82f6"}; width:{pct}%; height:100%; border-radius:100px;'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                add_amt = st.number_input(f"Add ₹ to Goal #{row['id']}", min_value=0.0,
                                          step=100.0, key=f"add_{row['id']}", label_visibility="collapsed")
                if st.button("Add", key=f"btn_{row['id']}"):
                    db_write("UPDATE savings_goals SET saved = saved + ? WHERE id = ?", (add_amt, row['id']))
                    st.rerun()
            with c3:
                if st.button("🗑 Delete", key=f"del_{row['id']}"):
                    db_write("DELETE FROM savings_goals WHERE id = ?", (row['id'],))
                    st.rerun()
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

# =========================
# ➕ ADD TRANSACTION
# =========================
elif menu == "➕ Add Transaction":
    st.markdown('<div class="page-title">Add Transaction</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Log a new expense</div>', unsafe_allow_html=True)

    with st.form("add_txn", clear_on_submit=True):
        r1c1, r1c2, r1c3 = st.columns(3)
        date   = r1c1.date_input("Date", value=datetime.today())
        cat    = r1c2.selectbox("Category", CATEGORIES)
        amt    = r1c3.number_input("Amount (₹)", min_value=0.01, step=10.0, format="%.2f")

        r2c1, r2c2, r2c3 = st.columns(3)
        desc   = r2c1.text_input("Description", placeholder="e.g. Grocery at D-Mart")
        pm     = r2c2.selectbox("Payment Method", PAYMENT_METHODS)
        recur  = r2c3.selectbox("Type", ["One-time", "Recurring"])

        submitted = st.form_submit_button("💾 Save Transaction", use_container_width=True)
        if submitted:
            if amt <= 0:
                st.error("Amount must be greater than zero.")
            elif not desc.strip():
                st.warning("Please add a description.")
            else:
                db_write(
                    "INSERT INTO expenses (date, category, amount, desc, payment_method, is_recurring) VALUES (?,?,?,?,?,?)",
                    (str(date), cat, amt, desc.strip(), pm, 1 if recur == "Recurring" else 0)
                )
                st.success(f"✅ ₹{amt:,.2f} logged under {cat}!")
                st.balloons()

    # Quick summary below form
    recent = db_select("SELECT date, category, amount, desc FROM expenses ORDER BY id DESC LIMIT 5")
    if not recent.empty:
        st.markdown('<div class="section-header">RECENTLY ADDED</div>', unsafe_allow_html=True)
        recent['amount'] = recent['amount'].apply(lambda x: f"₹{x:,.0f}")
        st.dataframe(recent, use_container_width=True, hide_index=True)

# =========================
# 📋 ALL TRANSACTIONS
# =========================
elif menu == "📋 All Transactions":
    st.markdown('<div class="page-title">All Transactions</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Browse, filter, and manage your records</div>', unsafe_allow_html=True)

    df = db_select("SELECT * FROM expenses ORDER BY date DESC, id DESC")

    if df.empty:
        st.info("No transactions yet.")
        st.stop()

    df['date'] = pd.to_datetime(df['date'])

    # Filters
    with st.expander("🔍 Filter Transactions"):
        fc1, fc2, fc3 = st.columns(3)
        cats = ["All"] + sorted(df['category'].unique().tolist())
        sel_cat = fc1.selectbox("Category", cats)
        min_d   = fc2.date_input("From", value=df['date'].min().date())
        max_d   = fc3.date_input("To",   value=df['date'].max().date())
        search  = st.text_input("Search Description", placeholder="Type to search...")

    filtered = df[
        (df['date'].dt.date >= min_d) &
        (df['date'].dt.date <= max_d)
    ]
    if sel_cat != "All":
        filtered = filtered[filtered['category'] == sel_cat]
    if search:
        filtered = filtered[filtered['desc'].str.contains(search, case=False, na=False)]

    # Stats row
    c1, c2, c3 = st.columns(3)
    c1.metric("Filtered Total",    f"₹{filtered['amount'].sum():,.0f}")
    c2.metric("Filtered Count",    len(filtered))
    c3.metric("Filtered Avg",      f"₹{filtered['amount'].mean():,.0f}" if not filtered.empty else "—")

    # Table
    display = filtered[['id','date','category','amount','desc','payment_method']].copy()
    display['date']   = display['date'].dt.strftime('%d %b %Y')
    display['amount'] = display['amount'].apply(lambda x: f"₹{x:,.0f}")
    st.dataframe(display, use_container_width=True, hide_index=True)

    # Export
    st.markdown(export_csv(filtered), unsafe_allow_html=True)

    # Delete
    st.markdown('<div class="section-header">DELETE A RECORD</div>', unsafe_allow_html=True)
    if not filtered.empty:
        del_id = st.number_input("Enter Transaction ID to delete", step=1,
                                 min_value=int(df['id'].min()), max_value=int(df['id'].max()))
        if st.button("🗑 Delete Transaction"):
            db_write("DELETE FROM expenses WHERE id = ?", (del_id,))
            st.success(f"Transaction #{del_id} deleted.")
            st.rerun()

# =========================
# ⚙️ SETTINGS
# =========================
elif menu == "⚙️ Settings":
    st.markdown('<div class="page-title">Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Manage your app data</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">DATA MANAGEMENT</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div style='background:#111827; border:1px solid #1e2d45; border-radius:14px; padding:20px;'>
            <div style='font-weight:700; margin-bottom:6px;'>🧹 Clear Expense Data</div>
            <div style='font-size:13px; color:#94a3b8; margin-bottom:14px;'>Delete all transaction records. Budgets and goals are preserved.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Clear Expenses", key="clr_exp"):
            db_write("DELETE FROM expenses", ())
            st.warning("All expense records cleared.")

    with c2:
        st.markdown("""
        <div style='background:#111827; border:1px solid #1e2d45; border-radius:14px; padding:20px;'>
            <div style='font-weight:700; margin-bottom:6px;'>💣 Factory Reset</div>
            <div style='font-size:13px; color:#94a3b8; margin-bottom:14px;'>Wipe everything: expenses, budgets, and savings goals.</div>
        </div>
        """, unsafe_allow_html=True)
        confirm = st.checkbox("I understand this is irreversible")
        if st.button("Factory Reset", key="factory", type="primary"):
            if confirm:
                db_write("DELETE FROM expenses", ())
                db_write("DELETE FROM budgets", ())
                db_write("DELETE FROM savings_goals", ())
                st.error("All data wiped. Refresh to start fresh.")
            else:
                st.warning("Please check the confirmation box first.")

    st.markdown('<div class="section-header">DATABASE INFO</div>', unsafe_allow_html=True)
    counts = {
        "Expenses":      db_select("SELECT COUNT(*) as c FROM expenses")['c'][0],
        "Budgets":       db_select("SELECT COUNT(*) as c FROM budgets")['c'][0],
        "Savings Goals": db_select("SELECT COUNT(*) as c FROM savings_goals")['c'][0],
    }
    for label, count in counts.items():
        st.markdown(f"""
        <div style='display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid #1e2d45; font-size:14px;'>
            <span style='color:#94a3b8;'>{label}</span>
            <span style='font-weight:700; font-family:JetBrains Mono, monospace;'>{count} records</span>
        </div>
        """, unsafe_allow_html=True)
