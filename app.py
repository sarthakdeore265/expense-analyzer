# ═══════════════════════════════════════════════════
#  NexFin Pro — Windows-Compatible Build v3.1
#  Run:  streamlit run nexfin_pro.py
#  Requires: pip install streamlit pandas plotly
# ═══════════════════════════════════════════════════

import sys
import os
import io
import base64
import calendar
import sqlite3
from datetime import datetime
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Windows console UTF-8 fix ──────────────────────
# Prevents UnicodeEncodeError when emoji/rupee symbols
# are printed to the Windows terminal (cp1252 default)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ═══════════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════════
st.set_page_config(
    page_title="NexFin Pro",
    page_icon="N",          # plain ASCII — avoids Windows font rendering issues in tab
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════
#  DATABASE — cross-platform path
#  Windows: C:\Users\<you>\NexFinPro\nexfin_pro.db
#  Linux/Mac: /home/<you>/NexFinPro/nexfin_pro.db
# ═══════════════════════════════════════════════════
_APP_DIR = Path.home() / "NexFinPro"
try:
    _APP_DIR.mkdir(parents=True, exist_ok=True)
except OSError as e:
    # Fallback to current working directory if home is not writable
    _APP_DIR = Path.cwd()

DB = str(_APP_DIR / "nexfin_pro.db")


def _connect():
    """Return a thread-safe SQLite connection."""
    return sqlite3.connect(DB, check_same_thread=False)


def init_db():
    with _connect() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                date            TEXT    NOT NULL,
                category        TEXT    NOT NULL,
                amount          REAL    NOT NULL,
                desc            TEXT    DEFAULT '',
                payment_method  TEXT    DEFAULT 'UPI',
                is_recurring    INTEGER DEFAULT 0,
                notes           TEXT    DEFAULT ''
            )""")
        c.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                category  TEXT PRIMARY KEY,
                limit_amt REAL NOT NULL
            )""")
        c.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                name     TEXT    NOT NULL,
                icon     TEXT    DEFAULT 'T',
                target   REAL    NOT NULL,
                saved    REAL    DEFAULT 0,
                deadline TEXT,
                color    TEXT    DEFAULT '#4f9eff'
            )""")


def sel(query, params=()):
    """Execute a SELECT and return a DataFrame."""
    with _connect() as c:
        return pd.read_sql(query, c, params=params)


def exe(query, params=()):
    """Execute a write query (INSERT / UPDATE / DELETE)."""
    with _connect() as c:
        c.execute(query, params)
        c.commit()


init_db()

# ═══════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════
CATS = [
    "Rent", "Food", "Transport", "Entertainment", "Shopping",
    "Bills", "Health", "Education", "Travel", "Fitness",
    "Gifts", "Dining", "Other"
]
PMS = ["UPI", "Card", "Cash", "Net Banking", "Wallet", "Crypto"]
GOAL_ICONS = ["Target", "Home", "Car", "Laptop", "Phone",
              "Travel", "Ring", "Education", "Beach", "Savings"]
GOAL_COLORS = ["#4f9eff", "#34d399", "#fbbf24", "#fb7185",
               "#a78bfa", "#22d3ee", "#f97316"]

CAT_EMOJI = {
    "Rent": "🏠", "Food": "🍱", "Transport": "🚗",
    "Entertainment": "🎬", "Shopping": "🛍", "Bills": "💡",
    "Health": "💊", "Education": "📚", "Travel": "✈",
    "Fitness": "💪", "Gifts": "🎁", "Dining": "🍕", "Other": "✨"
}


def cat_emoji(cat):
    """Return a safe emoji for a category — never raises on Windows."""
    return CAT_EMOJI.get(str(cat).strip(), "•")


# ═══════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════
def pct_delta(cur, prev):
    return ((cur - prev) / prev * 100) if prev else 0


def month_bounds(offset=0):
    n = datetime.now()
    m = (n.month - offset - 1) % 12 + 1
    y = n.year - ((n.month - offset - 1) // 12)
    first = datetime(y, m, 1).strftime("%Y-%m-%d")
    last  = datetime(y, m, calendar.monthrange(y, m)[1]).strftime("%Y-%m-%d")
    return first, last


def csv_download_link(df, label="Export CSV"):
    """
    Generate a CSV download link that works correctly on Windows.
    Uses utf-8-sig (BOM) so Excel on Windows renders the Rupee
    symbol and special characters without garbling.
    """
    csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
    b64 = base64.b64encode(csv_bytes).decode("utf-8")
    ts  = datetime.now().strftime("%Y%m%d_%H%M")
    return (
        f'<a href="data:text/csv;charset=utf-8;base64,{b64}" '
        f'download="nexfin_{ts}.csv">'
        f'<button style="background:linear-gradient(135deg,#2563eb,#1d4ed8);'
        f'color:#fff;border:none;padding:10px 22px;border-radius:10px;'
        f'cursor:pointer;font-family:Segoe UI,sans-serif;font-weight:600;'
        f'font-size:13px;box-shadow:0 2px 14px rgba(37,99,235,.35);">'
        f'{label}</button></a>'
    )


def chart_layout(**kw):
    base = dict(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, sans-serif", color="#8aa3bf", size=12),
        colorway=["#4f9eff", "#22d3ee", "#34d399", "#fbbf24",
                  "#fb7185", "#a78bfa", "#f97316"],
        margin=dict(l=12, r=12, t=44, b=12),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.05)",
            linecolor="rgba(255,255,255,0.05)",
            tickfont=dict(size=11)
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.05)",
            linecolor="rgba(255,255,255,0.05)",
            tickfont=dict(size=11)
        ),
        hoverlabel=dict(
            bgcolor="#162035",
            bordercolor="rgba(99,179,237,0.3)",
            font=dict(family="Segoe UI, sans-serif", size=13, color="#f0f6ff")
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(255,255,255,0.06)",
            font=dict(size=12)
        ),
        title_font=dict(size=14, color="#8aa3bf", family="Segoe UI, sans-serif"),
    )
    base.update(kw)
    return base


# ═══════════════════════════════════════════════════
#  CSS DESIGN SYSTEM
#  Fonts: Google Fonts with Segoe UI fallback so the
#  app still looks great if the CDN is blocked on
#  corporate / restricted Windows networks.
# ═══════════════════════════════════════════════════
DESIGN = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Space+Mono:wght@400;700&display=swap');

:root {
  --void:       #05070f;
  --deep:       #080c18;
  --surface:    #0c1220;
  --raised:     #111928;
  --float:      #162035;
  --border:     rgba(255,255,255,0.06);
  --border-hi:  rgba(99,179,237,0.3);
  --blue:       #4f9eff;
  --blue-dim:   #2563eb;
  --cyan:       #22d3ee;
  --emerald:    #34d399;
  --amber:      #fbbf24;
  --rose:       #fb7185;
  --violet:     #a78bfa;
  --t1: #f0f6ff;
  --t2: #8aa3bf;
  --t3: #3d5068;
  --t4: #1e2d40;
  --r-sm: 10px;  --r-md: 16px;  --r-lg: 22px;  --r-xl: 28px;
  --shadow-glow: 0 0 40px rgba(79,158,255,0.12);
}

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
  font-family: 'Outfit', 'Segoe UI', 'Calibri', sans-serif !important;
  background: var(--void) !important;
  color: var(--t1);
}

::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--t4); border-radius: 99px; }

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 3rem !important; max-width: 1440px !important; }

[data-testid="stSidebar"] {
  background: var(--deep) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .block-container { padding: 0 1.2rem 2rem !important; }

div[data-testid="stRadio"] > label { display: none !important; }
div[data-testid="stRadio"] > div { gap: 2px !important; display: flex; flex-direction: column; }
div[data-testid="stRadio"] label {
  border-radius: var(--r-sm) !important;
  padding: 11px 14px !important;
  cursor: pointer !important;
  transition: all 0.18s ease !important;
  color: var(--t2) !important;
  font-weight: 500 !important;
  font-size: 13.5px !important;
  border: 1px solid transparent !important;
  background: transparent !important;
}
div[data-testid="stRadio"] label:hover {
  background: var(--float) !important;
  color: var(--t1) !important;
  border-color: var(--border) !important;
}

[data-testid="stMetric"] {
  background: var(--raised) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-md) !important;
  padding: 20px 22px !important;
  transition: all 0.2s !important;
  position: relative; overflow: hidden;
}
[data-testid="stMetric"]:hover {
  border-color: var(--border-hi) !important;
  box-shadow: var(--shadow-glow) !important;
  transform: translateY(-1px);
}
[data-testid="stMetric"] label {
  color: var(--t3) !important; font-size: 10.5px !important;
  font-weight: 700 !important; text-transform: uppercase !important;
  letter-spacing: 1.8px !important;
}
[data-testid="stMetricValue"] {
  color: var(--t1) !important; font-size: 1.75rem !important;
  font-weight: 800 !important; letter-spacing: -0.5px !important;
}
[data-testid="stMetricDelta"] { font-size: 11.5px !important; }

.stButton > button {
  background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
  color: #fff !important; border: none !important;
  border-radius: var(--r-sm) !important; padding: 11px 26px !important;
  font-family: 'Outfit', 'Segoe UI', sans-serif !important;
  font-weight: 600 !important; font-size: 13.5px !important;
  transition: all 0.2s ease !important;
  box-shadow: 0 2px 16px rgba(37,99,235,0.35) !important;
}
.stButton > button:hover {
  background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 24px rgba(59,130,246,0.45) !important;
}

.stSelectbox > div > div,
.stNumberInput > div > div > input,
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stDateInput > div > div > input {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-sm) !important;
  color: var(--t1) !important;
  font-family: 'Outfit', 'Segoe UI', sans-serif !important;
  font-size: 14px !important;
}

[data-testid="stTabs"] [role="tablist"] {
  background: var(--surface) !important;
  border-radius: var(--r-sm) !important;
  padding: 4px !important; gap: 2px !important;
  border: 1px solid var(--border) !important;
}
[data-testid="stTabs"] [role="tab"] {
  color: var(--t2) !important; font-weight: 600 !important;
  font-size: 13px !important; border-radius: 8px !important;
  padding: 8px 18px !important; transition: all 0.2s !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
  background: var(--float) !important; color: var(--blue) !important;
}

[data-testid="stForm"] {
  background: var(--raised) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-lg) !important; padding: 28px !important;
}

details {
  background: var(--raised) !important; border: 1px solid var(--border) !important;
  border-radius: var(--r-md) !important; overflow: hidden !important;
}
details:hover { border-color: var(--border-hi) !important; }
summary { padding: 14px 18px !important; color: var(--t1) !important;
          font-weight: 600 !important; font-size: 14px !important; }

[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important;
  border-radius: var(--r-md) !important; overflow: hidden !important;
}
[data-testid="stDataFrame"] th {
  background: var(--surface) !important; color: var(--t3) !important;
  font-size: 10.5px !important; font-weight: 700 !important;
  text-transform: uppercase !important; letter-spacing: 1.5px !important;
}
[data-testid="stDataFrame"] td {
  background: var(--raised) !important; color: var(--t2) !important;
  font-size: 13.5px !important;
}
[data-testid="stDataFrame"] tr:hover td { background: var(--float) !important; }

.stProgress > div > div > div { border-radius: 99px !important; }
.stProgress > div > div { background: var(--float) !important; border-radius: 99px !important; }

[data-testid="stSuccess"] { background: rgba(52,211,153,0.08) !important; border-left: 3px solid var(--emerald) !important; }
[data-testid="stWarning"] { background: rgba(251,191,36,0.08) !important;  border-left: 3px solid var(--amber)   !important; }
[data-testid="stError"]   { background: rgba(251,113,133,0.08) !important; border-left: 3px solid var(--rose)    !important; }
[data-testid="stInfo"]    { background: rgba(79,158,255,0.08) !important;  border-left: 3px solid var(--blue)    !important; }

@keyframes fadeUp { from{opacity:0;transform:translateY(14px)} to{opacity:1;transform:translateY(0)} }

.page-head {
  padding: 28px 0 20px; border-bottom: 1px solid var(--border);
  margin-bottom: 28px; animation: fadeUp .4s ease;
}
.page-head .eyebrow {
  font-size: 10px; font-weight: 700; letter-spacing: 3px;
  text-transform: uppercase; color: var(--blue); margin-bottom: 6px;
}
.page-head h1 {
  font-size: 2.1rem; font-weight: 900; color: var(--t1);
  margin: 0 0 4px; letter-spacing: -1px; line-height: 1.1;
}
.page-head p { font-size: 14px; color: var(--t2); margin: 0; }

.hero-card {
  background: linear-gradient(135deg,#0f1e3d 0%,#0a1628 50%,#0c1a35 100%);
  border: 1px solid rgba(79,158,255,0.2); border-radius: var(--r-xl);
  padding: 32px 36px; position: relative; overflow: hidden; animation: fadeUp .5s ease;
}
.hero-card::before {
  content:''; position:absolute; top:-60px; right:-60px; width:280px; height:280px;
  background:radial-gradient(circle,rgba(79,158,255,.12) 0%,transparent 65%);
  pointer-events:none;
}
.hero-card .label {
  font-size:10px; font-weight:700; letter-spacing:3px;
  text-transform:uppercase; color:rgba(147,197,253,.7); margin-bottom:8px;
}
.hero-card .amount {
  font-size:3rem; font-weight:900; color:#fff;
  letter-spacing:-2px; line-height:1; margin-bottom:20px;
}
.hero-card .stats-row { display:flex; gap:32px; flex-wrap:wrap; }
.hero-card .stat-item .stat-label {
  font-size:10px; color:rgba(147,197,253,.6);
  text-transform:uppercase; letter-spacing:1.5px; margin-bottom:3px;
}
.hero-card .stat-item .stat-val { font-size:1.25rem; font-weight:800; color:#fff; }

.stat-mini {
  background:var(--raised); border:1px solid var(--border); border-radius:var(--r-md);
  padding:18px 20px; transition:all .2s; animation:fadeUp .5s ease both;
  position:relative; overflow:hidden;
}
.stat-mini:hover { border-color:var(--border-hi); box-shadow:var(--shadow-glow); transform:translateY(-2px); }
.stat-mini .sm-label { font-size:10px; font-weight:700; letter-spacing:2px; text-transform:uppercase; color:var(--t3); margin-bottom:10px; }
.stat-mini .sm-value { font-size:1.6rem; font-weight:900; color:var(--t1); letter-spacing:-0.5px; line-height:1.1; }
.stat-mini .sm-sub   { font-size:12px; color:var(--t2); margin-top:5px; }
.stat-mini .sm-accent { position:absolute; top:0; right:0; width:3px; height:100%; border-radius:0 var(--r-md) var(--r-md) 0; }

.sec-label {
  font-size:10px; font-weight:700; letter-spacing:2.5px; text-transform:uppercase;
  color:var(--t3); margin:30px 0 14px; display:flex; align-items:center; gap:10px;
}
.sec-label::after { content:''; flex:1; height:1px; background:linear-gradient(90deg,var(--border),transparent); }

.bud-row {
  background:var(--raised); border:1px solid var(--border); border-radius:var(--r-md);
  padding:18px 22px; margin-bottom:10px; transition:all .2s; animation:fadeUp .4s ease both;
}
.bud-row:hover { border-color:var(--border-hi); background:var(--float); }
.bud-row .bud-top { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; }
.bud-row .bud-name { font-size:15px; font-weight:700; color:var(--t1); }
.bud-row .bud-nums { font-family:'Courier New',Consolas,monospace; font-size:12px; color:var(--t2); }
.bud-track { height:6px; background:var(--float); border-radius:99px; overflow:hidden; margin-bottom:8px; }
.bud-fill  { height:100%; border-radius:99px; transition:width .6s cubic-bezier(.4,0,.2,1); }
.bud-foot  { display:flex; justify-content:space-between; font-size:11.5px; }

.pill { display:inline-flex; align-items:center; gap:5px; padding:3px 10px; border-radius:99px; font-size:10.5px; font-weight:700; letter-spacing:.4px; text-transform:uppercase; }
.pill-green  { background:rgba(52,211,153,.12);  color:var(--emerald); border:1px solid rgba(52,211,153,.2); }
.pill-amber  { background:rgba(251,191,36,.12);  color:var(--amber);   border:1px solid rgba(251,191,36,.2); }
.pill-rose   { background:rgba(251,113,133,.12); color:var(--rose);    border:1px solid rgba(251,113,133,.2); }

.goal-card {
  background:var(--raised); border:1px solid var(--border); border-radius:var(--r-lg);
  padding:22px 24px; margin-bottom:12px; transition:all .2s; animation:fadeUp .5s ease both;
}
.goal-card:hover { border-color:var(--border-hi); box-shadow:var(--shadow-glow); }

.insight {
  background:var(--raised); border:1px solid var(--border); border-left:2px solid var(--blue);
  border-radius:var(--r-md); padding:14px 18px; margin-bottom:10px;
  font-size:13.5px; color:var(--t2); line-height:1.55;
  animation:fadeUp .4s ease both; transition:all .2s;
}
.insight:hover { background:var(--float); color:var(--t1); }
.insight b { color:var(--t1); }

.txn-row { display:flex; align-items:center; gap:14px; padding:12px 16px; border-radius:var(--r-sm); transition:background .15s; }
.txn-row:hover { background:var(--float); }
.txn-icon { width:38px; height:38px; background:var(--float); border:1px solid var(--border); border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:17px; flex-shrink:0; }
.txn-body { flex:1; min-width:0; }
.txn-desc { font-size:14px; font-weight:600; color:var(--t1); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.txn-meta { font-size:11.5px; color:var(--t3); margin-top:1px; }
.txn-amt  { font-family:'Courier New',Consolas,monospace; font-size:14px; font-weight:700; color:var(--rose); white-space:nowrap; }

.brand { padding:24px 16px 16px; margin-bottom:8px; }
.brand-mark { display:flex; align-items:center; gap:10px; }
.brand-icon { width:36px; height:36px; background:linear-gradient(135deg,#2563eb,#1d4ed8); border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:16px; font-weight:900; color:#fff; box-shadow:0 4px 16px rgba(37,99,235,.4); }
.brand-name { font-size:17px; font-weight:900; color:var(--t1); letter-spacing:-.3px; }
.brand-tag  { font-size:10px; color:var(--t3); letter-spacing:2px; text-transform:uppercase; margin-top:1px; }

.hdiv { height:1px; background:var(--border); margin:12px 0; }
.nav-label { font-size:9.5px; font-weight:700; letter-spacing:2.5px; text-transform:uppercase; color:var(--t4); padding:12px 4px 6px; }

.q-stat { background:var(--surface); border:1px solid var(--border); border-radius:var(--r-sm); padding:12px 14px; margin-bottom:6px; }
.q-stat-label { font-size:10.5px; color:var(--t3); font-weight:600; letter-spacing:.5px; }
.q-stat-val { font-size:16px; font-weight:800; color:var(--t1); margin-top:1px; font-family:'Courier New',Consolas,monospace; }

.chart-wrap { background:var(--raised); border:1px solid var(--border); border-radius:var(--r-lg); padding:8px; transition:border-color .2s; }
.chart-wrap:hover { border-color:var(--border-hi); }

.empty-state { text-align:center; padding:60px 40px; background:var(--raised); border:1px dashed var(--border); border-radius:var(--r-xl); animation:fadeUp .5s ease; }
.empty-state .empty-icon { font-size:40px; margin-bottom:14px; }
.empty-state h3 { font-size:18px; font-weight:700; color:var(--t1); margin:0 0 8px; }
.empty-state p  { font-size:14px; color:var(--t2); margin:0; }

.setting-block { background:var(--raised); border:1px solid var(--border); border-radius:var(--r-lg); padding:22px 24px; margin-bottom:12px; transition:border-color .2s; }
.setting-block:hover { border-color:var(--border-hi); }
.setting-block h4 { font-size:15px; font-weight:700; color:var(--t1); margin:0 0 6px; }
.setting-block p  { font-size:13px; color:var(--t2); margin:0 0 16px; }
</style>
"""
st.markdown(DESIGN, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="brand">
      <div class="brand-mark">
        <div class="brand-icon">N</div>
        <div>
          <div class="brand-name">NexFin</div>
          <div class="brand-tag">Pro Edition</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-label">Navigation</div>', unsafe_allow_html=True)
    menu = st.radio("", [
        "  Dashboard",
        "  Analytics",
        "  Budgets",
        "  Savings Goals",
        "  Add Transaction",
        "  All Transactions",
        "  Settings"
    ])

    st.markdown('<div class="hdiv"></div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-label">Quick Stats</div>', unsafe_allow_html=True)

    df_s = sel("SELECT * FROM expenses")
    if not df_s.empty:
        s0, e0 = month_bounds(0)
        this_m = df_s[df_s["date"].between(s0, e0)]["amount"].sum()
        st.markdown(f"""
        <div class="q-stat">
          <div class="q-stat-label">This Month</div>
          <div class="q-stat-val">Rs. {this_m:,.0f}</div>
        </div>
        <div class="q-stat">
          <div class="q-stat-label">All Time</div>
          <div class="q-stat-val">Rs. {df_s['amount'].sum():,.0f}</div>
        </div>
        <div class="q-stat">
          <div class="q-stat-label">Transactions</div>
          <div class="q-stat-val">{len(df_s)}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="font-size:12px;color:#3d5068;padding:4px;">No data yet.</div>',
            unsafe_allow_html=True
        )

    st.markdown('<div class="hdiv"></div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-size:10px;color:#1e2d40;text-align:center;padding-bottom:8px;">'
        f'v3.1-win &middot; {datetime.now().strftime("%b %Y")}</div>',
        unsafe_allow_html=True
    )

# Derive page from radio label (strip leading spaces)
page = menu.strip()


# ═══════════════════════════════════════════════════
#  DASHBOARD
# ═══════════════════════════════════════════════════
if page == "Dashboard":
    st.markdown(
        '<div class="page-head">'
        '<div class="eyebrow">Overview</div>'
        '<h1>Dashboard</h1>'
        '<p>Your complete financial picture &mdash; at a glance.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    df = sel("SELECT * FROM expenses ORDER BY date DESC")

    if df.empty:
        st.markdown(
            '<div class="empty-state">'
            '<div class="empty-icon">&#128202;</div>'
            '<h3>Nothing to show yet</h3>'
            '<p>Add your first transaction to see your dashboard come alive.</p>'
            '</div>',
            unsafe_allow_html=True
        )
        st.stop()

    df["date"] = pd.to_datetime(df["date"])
    s0, e0 = month_bounds(0)
    s1, e1 = month_bounds(1)
    this_df = df[df["date"].between(s0, e0)]
    prev_df = df[df["date"].between(s1, e1)]
    this_t  = this_df["amount"].sum()
    prev_t  = prev_df["amount"].sum()
    delta   = pct_delta(this_t, prev_t)
    avg_d   = this_df.groupby("date")["amount"].sum().mean() if not this_df.empty else 0
    top_cat = (
        this_df.groupby("category")["amount"].sum().idxmax()
        if not this_df.empty else "—"
    )

    delta_color = "#fb7185" if delta > 0 else "#34d399"
    delta_arrow = "&#9650;" if delta > 0 else "&#9660;"
    top_em = cat_emoji(top_cat)

    st.markdown(f"""
    <div class="hero-card">
      <div class="label">Monthly Spend &middot; {datetime.now().strftime('%B %Y')}</div>
      <div class="amount">Rs. {this_t:,.0f}</div>
      <div class="stats-row">
        <div class="stat-item">
          <div class="stat-label">vs Last Month</div>
          <div class="stat-val" style="color:{delta_color}">
            {delta_arrow} {abs(delta):.1f}%
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-label">Daily Avg</div>
          <div class="stat-val">Rs. {avg_d:,.0f}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">Transactions</div>
          <div class="stat-val">{len(this_df)}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">Top Category</div>
          <div class="stat-val">{top_em} {top_cat}</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Stat mini cards ──
    cols = st.columns(4)
    stats = [
        ("LIFETIME TOTAL",  f"Rs. {df['amount'].sum():,.0f}",  f"{len(df)} records",  "#4f9eff"),
        ("AVG TRANSACTION", f"Rs. {df['amount'].mean():,.0f}", "per expense",          "#22d3ee"),
        ("LARGEST SPEND",   f"Rs. {df['amount'].max():,.0f}",  df.loc[df["amount"].idxmax(), "category"], "#fbbf24"),
        ("CATEGORIES",      str(df["category"].nunique()),     "active",               "#34d399"),
    ]
    for i, (lbl, val, sub, clr) in enumerate(stats):
        with cols[i]:
            st.markdown(f"""
            <div class="stat-mini" style="animation-delay:{i*0.08}s">
              <div class="sm-accent" style="background:{clr}"></div>
              <div class="sm-label">{lbl}</div>
              <div class="sm-value">{val}</div>
              <div class="sm-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    # ── Charts ──
    st.markdown('<div class="sec-label">Spending Flow</div>', unsafe_allow_html=True)
    cl, cr = st.columns([3, 2])

    with cl:
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        daily = df.groupby(df["date"].dt.date)["amount"].sum().reset_index()
        daily.columns = ["date", "amount"]
        daily["ma7"] = daily["amount"].rolling(7, min_periods=1).mean()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily["date"], y=daily["amount"], name="Daily", mode="lines",
            line=dict(color="rgba(79,158,255,0.4)", width=1),
            fill="tozeroy", fillcolor="rgba(79,158,255,0.05)"
        ))
        fig.add_trace(go.Scatter(
            x=daily["date"], y=daily["ma7"], name="7-Day Avg", mode="lines",
            line=dict(color="#4f9eff", width=2.5)
        ))
        fig.update_layout(title="Daily Spending + 7-Day Average", **chart_layout())
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with cr:
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        cat_df = df.groupby("category")["amount"].sum().reset_index()
        fig2 = px.pie(cat_df, values="amount", names="category",
                      hole=0.62, title="Category Split")
        fig2.update_traces(textposition="outside", textfont_size=11,
                           marker=dict(line=dict(color="#080c18", width=2)))
        fig2.update_layout(**chart_layout())
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="sec-label">Month-over-Month</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    monthly = df.groupby(df["date"].dt.to_period("M"))["amount"].sum().reset_index()
    monthly["date"] = monthly["date"].astype(str)
    fig3 = go.Figure(go.Bar(
        x=monthly["date"], y=monthly["amount"],
        marker=dict(
            color=monthly["amount"],
            colorscale=[[0, "#162035"], [0.5, "#2563eb"], [1, "#4f9eff"]],
            line=dict(width=0)
        ),
        text=monthly["amount"].apply(lambda x: f"Rs.{x:,.0f}"),
        textposition="outside", textfont=dict(size=11, color="#8aa3bf")
    ))
    fig3.update_layout(title="Monthly Spending History", **chart_layout())
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Recent transactions ──
    st.markdown('<div class="sec-label">Recent Transactions</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="background:var(--raised);border:1px solid var(--border);'
        'border-radius:var(--r-lg);padding:8px 6px;">',
        unsafe_allow_html=True
    )
    for _, r in df.head(8).iterrows():
        em   = cat_emoji(r["category"])
        desc = str(r["desc"]) if r["desc"] else str(r["category"])
        pm   = str(r.get("payment_method", "—"))
        st.markdown(f"""
        <div class="txn-row">
          <div class="txn-icon">{em}</div>
          <div class="txn-body">
            <div class="txn-desc">{desc}</div>
            <div class="txn-meta">{r['category']} &middot; {r['date'].strftime('%d %b %Y')} &middot; {pm}</div>
          </div>
          <div class="txn-amt">-Rs.{r['amount']:,.0f}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
#  ANALYTICS
# ═══════════════════════════════════════════════════
elif page == "Analytics":
    st.markdown(
        '<div class="page-head"><div class="eyebrow">Intelligence</div>'
        '<h1>Deep Analytics</h1>'
        '<p>Pattern recognition, trends, and actionable insights.</p></div>',
        unsafe_allow_html=True
    )
    df = sel("SELECT * FROM expenses")
    if df.empty:
        st.markdown(
            '<div class="empty-state"><div class="empty-icon">&#128200;</div>'
            '<h3>No data yet</h3><p>Add transactions to unlock analytics.</p></div>',
            unsafe_allow_html=True
        )
        st.stop()

    df["date"]  = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["dow"]   = df["date"].dt.day_name()

    tab1, tab2, tab3 = st.tabs(["Time Patterns", "Category Breakdown", "Insights"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
            dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
            dow_df = df.groupby("dow")["amount"].sum().reindex(dow_order).reset_index()
            fig = px.bar(dow_df, x="dow", y="amount", title="Spend by Day of Week",
                         color="amount",
                         color_continuous_scale=[[0,"#162035"],[1,"#4f9eff"]])
            fig.update_layout(**chart_layout(), showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
            mc = df.groupby(["month","category"])["amount"].sum().reset_index()
            fig2 = px.line(mc, x="month", y="amount", color="category",
                           title="Category Trends", markers=True)
            fig2.update_layout(**chart_layout())
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="chart-wrap" style="margin-top:12px">', unsafe_allow_html=True)
        df_c = df.sort_values("date").copy()
        df_c["cumulative"] = df_c["amount"].cumsum()
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=df_c["date"], y=df_c["cumulative"],
            mode="lines", fill="tozeroy",
            line=dict(color="#22d3ee", width=2.5),
            fillcolor="rgba(34,211,238,0.06)", name="Cumulative"
        ))
        fig3.update_layout(title="Cumulative Lifetime Spending", **chart_layout())
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
            cat_t = df.groupby("category")["amount"].sum().sort_values().reset_index()
            fig = px.bar(cat_t, x="amount", y="category", orientation="h",
                         title="Total per Category",
                         color="amount",
                         color_continuous_scale=[[0,"#162035"],[1,"#4f9eff"]])
            fig.update_layout(**chart_layout(), showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
            fig2 = px.sunburst(df, path=["category","desc"], values="amount",
                               title="Category to Item Breakdown",
                               color_discrete_sequence=["#4f9eff","#22d3ee","#34d399",
                                                        "#fbbf24","#fb7185","#a78bfa"])
            fig2.update_layout(**chart_layout())
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        if df["payment_method"].notna().any():
            st.markdown('<div class="chart-wrap" style="margin-top:12px">', unsafe_allow_html=True)
            pm = df.groupby("payment_method")["amount"].sum().reset_index()
            fig3 = px.pie(pm, values="amount", names="payment_method",
                          hole=0.5, title="By Payment Method",
                          color_discrete_sequence=["#4f9eff","#22d3ee","#34d399",
                                                   "#fbbf24","#fb7185","#a78bfa"])
            fig3.update_layout(**chart_layout())
            st.plotly_chart(fig3, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        top_cat  = df.groupby("category")["amount"].sum().idxmax()
        top_amt  = df.groupby("category")["amount"].sum().max()
        avg_txn  = df["amount"].mean()
        big_row  = df.loc[df["amount"].idxmax()]
        freq_cat = df["category"].value_counts().idxmax()
        mo_avg   = df.groupby(df["date"].dt.to_period("M"))["amount"].sum().mean()
        wknd     = df[df["dow"].isin(["Saturday","Sunday"])]["amount"].sum()
        wkdy     = df[~df["dow"].isin(["Saturday","Sunday"])]["amount"].sum()
        wknd_pct = wknd / (wknd + wkdy) * 100 if (wknd + wkdy) > 0 else 0
        recur_pct = (
            df[df["is_recurring"] == 1]["amount"].sum() / df["amount"].sum() * 100
            if not df.empty else 0
        )

        big_desc = str(big_row["desc"]) if big_row["desc"] else str(big_row["category"])
        wknd_tip = "High — consider reducing discretionary spend." if wknd_pct > 35 else "Healthy weekend balance."
        rec_tip  = "Audit subscriptions — may have hidden costs." if recur_pct > 30 else "Good balance of recurring vs one-time."

        insights = [
            f"<b>{top_cat}</b> is your biggest spend category at Rs.{top_amt:,.0f}. Consider reviewing allocation.",
            f"Average transaction: <b>Rs.{avg_txn:,.0f}</b>. Purchases above this are significant.",
            f"Largest single expense: <b>Rs.{big_row['amount']:,.0f}</b> &mdash; {big_desc}.",
            f"<b>{freq_cat}</b> appears most frequently &mdash; likely a daily or recurring pattern.",
            f"Monthly average: <b>Rs.{mo_avg:,.0f}</b>. Annual projection: Rs.{mo_avg*12:,.0f}.",
            f"<b>{wknd_pct:.0f}%</b> of spending on weekends. {wknd_tip}",
            f"<b>{recur_pct:.0f}%</b> recurring expenses. {rec_tip}",
        ]
        st.markdown('<div class="sec-label">Insights</div>', unsafe_allow_html=True)
        for i, txt in enumerate(insights):
            st.markdown(
                f'<div class="insight" style="animation-delay:{i*0.06}s">{txt}</div>',
                unsafe_allow_html=True
            )


# ═══════════════════════════════════════════════════
#  BUDGETS
# ═══════════════════════════════════════════════════
elif page == "Budgets":
    st.markdown(
        '<div class="page-head"><div class="eyebrow">Control</div>'
        '<h1>Budget Center</h1>'
        '<p>Set limits, track actuals, and stay in the green.</p></div>',
        unsafe_allow_html=True
    )

    with st.expander("Add / Update a Budget"):
        bc1, bc2, bc3 = st.columns([2, 2, 1])
        b_cat   = bc1.selectbox("Category", CATS)
        b_limit = bc2.number_input("Monthly Limit (Rs.)", min_value=0.0, step=500.0, format="%.0f")
        bc3.markdown("<br>", unsafe_allow_html=True)
        if bc3.button("Save"):
            exe("INSERT OR REPLACE INTO budgets VALUES (?,?)", (b_cat, b_limit))
            st.success(f"Budget saved: {b_cat} at Rs.{b_limit:,.0f}/mo")

    s0, e0 = month_bounds(0)
    budgets  = sel("SELECT * FROM budgets")
    expenses = sel(
        f"SELECT category, SUM(amount) as spent FROM expenses "
        f"WHERE date BETWEEN '{s0}' AND '{e0}' GROUP BY category"
    )

    if budgets.empty:
        st.markdown(
            '<div class="empty-state"><div class="empty-icon">&#127919;</div>'
            '<h3>No budgets set</h3><p>Create your first budget above.</p></div>',
            unsafe_allow_html=True
        )
    else:
        merged = pd.merge(budgets, expenses, on="category", how="left").fillna(0)
        merged["remaining"] = merged["limit_amt"] - merged["spent"]
        merged["pct"] = (
            merged["spent"] / merged["limit_amt"].replace(0, 1) * 100
        ).clip(0, 100)

        total_budget = merged["limit_amt"].sum()
        total_spent  = merged["spent"].sum()
        over_count   = (merged["remaining"] < 0).sum()

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Budget", f"Rs. {total_budget:,.0f}")
        c2.metric("Total Spent",  f"Rs. {total_spent:,.0f}",
                  f"{total_spent/total_budget*100:.0f}% used" if total_budget else "—")
        c3.metric("Over Budget",  f"{over_count} cats",
                  "Attention needed" if over_count else "All clear")

        st.markdown('<div class="sec-label">Category Status</div>', unsafe_allow_html=True)
        for _, row in merged.sort_values("pct", ascending=False).iterrows():
            pct   = row["pct"]
            color = "#34d399" if pct < 70 else "#fbbf24" if pct < 90 else "#fb7185"
            tag, pill_cls = (
                ("ON TRACK", "pill-green") if pct < 70 else
                ("WARNING",  "pill-amber") if pct < 90 else
                ("OVER",     "pill-rose")
            )
            rem_col = "#fb7185" if row["remaining"] < 0 else "#34d399"
            rem_txt = (
                f"Over Rs.{abs(row['remaining']):,.0f}"
                if row["remaining"] < 0
                else f"Rs.{row['remaining']:,.0f} left"
            )
            st.markdown(f"""
            <div class="bud-row">
              <div class="bud-top">
                <div class="bud-name">{cat_emoji(row['category'])} {row['category']}</div>
                <div style="display:flex;align-items:center;gap:10px">
                  <span class="bud-nums">Rs.{row['spent']:,.0f} / Rs.{row['limit_amt']:,.0f}</span>
                  <span class="pill {pill_cls}">{tag}</span>
                </div>
              </div>
              <div class="bud-track">
                <div class="bud-fill" style="width:{pct}%;background:{color}"></div>
              </div>
              <div class="bud-foot">
                <span style="color:var(--t3)">{pct:.1f}% used</span>
                <span style="color:{rem_col};font-family:'Courier New',monospace;font-size:11.5px">{rem_txt}</span>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="sec-label">Budget vs Actual</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Budget", x=merged["category"], y=merged["limit_amt"],
            marker_color="rgba(79,158,255,0.2)", marker_line_width=0
        ))
        fig.add_trace(go.Bar(
            name="Spent", x=merged["category"], y=merged["spent"],
            marker_color="#4f9eff", marker_line_width=0
        ))
        fig.update_layout(barmode="group", title="Budget vs Actual This Month",
                          **chart_layout())
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("Remove a Budget"):
            del_cat = st.selectbox("Category to remove", merged["category"].tolist())
            if st.button("Delete Budget"):
                exe("DELETE FROM budgets WHERE category=?", (del_cat,))
                st.success("Budget removed.")
                st.rerun()


# ═══════════════════════════════════════════════════
#  SAVINGS GOALS
# ═══════════════════════════════════════════════════
elif page == "Savings Goals":
    st.markdown(
        '<div class="page-head"><div class="eyebrow">Goals</div>'
        '<h1>Savings Goals</h1>'
        '<p>Define milestones. Track progress. Reach them.</p></div>',
        unsafe_allow_html=True
    )

    with st.expander("Create New Goal"):
        g1, g2, g3 = st.columns(3)
        gname    = g1.text_input("Goal Name", placeholder="e.g. Emergency Fund")
        gtarget  = g2.number_input("Target (Rs.)", min_value=100.0, step=1000.0, format="%.0f")
        gsaved   = g3.number_input("Already Saved (Rs.)", min_value=0.0, step=100.0, format="%.0f")
        g4, g5, g6 = st.columns(3)
        gdeadline = g4.date_input("Target Date")
        gcolor    = g5.selectbox("Accent Color", GOAL_COLORS)
        g6.markdown("")
        if g6.button("Create Goal"):
            if gname.strip():
                exe(
                    "INSERT INTO goals (name,icon,target,saved,deadline,color) VALUES (?,?,?,?,?,?)",
                    (gname.strip(), "T", gtarget, gsaved, str(gdeadline), gcolor)
                )
                st.success(f"Goal '{gname}' created!")
                st.rerun()
            else:
                st.error("Please enter a goal name.")

    goals = sel("SELECT * FROM goals")
    if goals.empty:
        st.markdown(
            '<div class="empty-state"><div class="empty-icon">&#127942;</div>'
            '<h3>No goals yet</h3><p>Set your first savings target above.</p></div>',
            unsafe_allow_html=True
        )
    else:
        total_t = goals["target"].sum()
        total_s = goals["saved"].sum()
        oc1, oc2, oc3 = st.columns(3)
        oc1.metric("Total Goals",      str(len(goals)))
        oc2.metric("Total Saved",      f"Rs. {total_s:,.0f}", f"of Rs. {total_t:,.0f}")
        oc3.metric("Overall Progress", f"{total_s/total_t*100:.0f}%" if total_t else "—")

        st.markdown('<div class="sec-label">Your Goals</div>', unsafe_allow_html=True)
        for _, row in goals.iterrows():
            pct = min((row["saved"] / row["target"]) * 100, 100) if row["target"] else 0
            deadline_str = ""
            days_left = None
            if row["deadline"]:
                dl = pd.to_datetime(row["deadline"])
                days_left = (dl - datetime.now()).days
                deadline_str = f"Due {dl.strftime('%d %b %Y')}"
                deadline_str += f" ({days_left}d left)" if days_left >= 0 else " (Overdue)"

            bar_color = "#34d399" if pct >= 100 else row["color"]
            remaining_txt = "Completed!" if pct >= 100 else f"Rs.{row['target']-row['saved']:,.0f} to go"
            overdue_txt   = "Overdue" if (days_left is not None and days_left < 0) else ""

            c_main, c_act = st.columns([5, 1])
            with c_main:
                st.markdown(f"""
                <div class="goal-card" style="border-left:3px solid {row['color']}">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px">
                    <div>
                      <div style="font-size:16px;font-weight:800;color:var(--t1)">{row['name']}</div>
                      <div style="font-size:12px;color:var(--t3);margin-top:2px">{deadline_str}</div>
                    </div>
                    <div style="text-align:right">
                      <div style="font-size:1.6rem;font-weight:900;color:var(--t1)">{pct:.0f}%</div>
                      <div style="font-family:'Courier New',monospace;font-size:11px;color:var(--t2)">
                        Rs.{row['saved']:,.0f} / Rs.{row['target']:,.0f}
                      </div>
                    </div>
                  </div>
                  <div style="background:var(--float);border-radius:99px;height:8px;overflow:hidden">
                    <div style="background:{bar_color};width:{pct}%;height:100%;border-radius:99px;
                                transition:width .6s cubic-bezier(.4,0,.2,1)"></div>
                  </div>
                  <div style="display:flex;justify-content:space-between;margin-top:8px;font-size:12px;color:var(--t3)">
                    <span>{remaining_txt}</span>
                    <span style="color:#fb7185">{overdue_txt}</span>
                  </div>
                </div>""", unsafe_allow_html=True)
            with c_act:
                add_v = st.number_input(
                    "Add", min_value=0.0, step=100.0,
                    key=f"g_add_{row['id']}", label_visibility="collapsed",
                    placeholder="Add Rs."
                )
                if st.button("Add", key=f"g_btn_{row['id']}"):
                    exe("UPDATE goals SET saved=saved+? WHERE id=?", (add_v, row["id"]))
                    st.rerun()
                if st.button("Del", key=f"g_del_{row['id']}"):
                    exe("DELETE FROM goals WHERE id=?", (row["id"],))
                    st.rerun()


# ═══════════════════════════════════════════════════
#  ADD TRANSACTION
# ═══════════════════════════════════════════════════
elif page == "Add Transaction":
    st.markdown(
        '<div class="page-head"><div class="eyebrow">Log</div>'
        '<h1>Add Transaction</h1>'
        '<p>Record a new expense in seconds.</p></div>',
        unsafe_allow_html=True
    )

    with st.form("add_txn", clear_on_submit=True):
        st.markdown(
            '<div style="font-size:11px;font-weight:700;letter-spacing:2px;'
            'text-transform:uppercase;color:var(--t3);margin-bottom:8px">BASIC DETAILS</div>',
            unsafe_allow_html=True
        )
        r1, r2, r3 = st.columns(3)
        t_date = r1.date_input("Date", value=datetime.today())
        t_cat  = r2.selectbox("Category", CATS)
        t_amt  = r3.number_input("Amount (Rs.)", min_value=0.01, step=10.0, format="%.2f")

        st.markdown(
            '<div style="font-size:11px;font-weight:700;letter-spacing:2px;'
            'text-transform:uppercase;color:var(--t3);margin:12px 0 8px">ADDITIONAL INFO</div>',
            unsafe_allow_html=True
        )
        r4, r5, r6 = st.columns(3)
        t_desc  = r4.text_input("Description", placeholder="e.g. Monthly rent payment")
        t_pm    = r5.selectbox("Payment Method", PMS)
        t_recur = r6.selectbox("Type", ["One-time", "Recurring"])
        t_notes = st.text_area("Notes (optional)", placeholder="Any extra details...", height=80)

        submitted = st.form_submit_button("Save Transaction", use_container_width=True)
        if submitted:
            if t_amt <= 0:
                st.error("Amount must be greater than 0.")
            elif not t_desc.strip():
                st.warning("Please add a description.")
            else:
                exe(
                    "INSERT INTO expenses "
                    "(date,category,amount,desc,payment_method,is_recurring,notes) "
                    "VALUES (?,?,?,?,?,?,?)",
                    (str(t_date), t_cat, t_amt, t_desc.strip(), t_pm,
                     1 if t_recur == "Recurring" else 0, t_notes)
                )
                st.success(f"Rs.{t_amt:,.2f} logged under {t_cat}")
                st.balloons()

    recent = sel("SELECT date,category,amount,desc,payment_method FROM expenses ORDER BY id DESC LIMIT 6")
    if not recent.empty:
        st.markdown('<div class="sec-label">Recently Added</div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="background:var(--raised);border:1px solid var(--border);'
            'border-radius:var(--r-lg);padding:8px 6px;">',
            unsafe_allow_html=True
        )
        for _, r in recent.iterrows():
            em   = cat_emoji(r["category"])
            desc = str(r["desc"]) if r["desc"] else str(r["category"])
            pm   = str(r.get("payment_method", "—"))
            st.markdown(f"""
            <div class="txn-row">
              <div class="txn-icon">{em}</div>
              <div class="txn-body">
                <div class="txn-desc">{desc}</div>
                <div class="txn-meta">{r['category']} &middot; {r['date']} &middot; {pm}</div>
              </div>
              <div class="txn-amt">-Rs.{r['amount']:,.0f}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
#  ALL TRANSACTIONS
# ═══════════════════════════════════════════════════
elif page == "All Transactions":
    st.markdown(
        '<div class="page-head"><div class="eyebrow">Records</div>'
        '<h1>All Transactions</h1>'
        '<p>Browse, filter, search, and manage every record.</p></div>',
        unsafe_allow_html=True
    )

    df = sel("SELECT * FROM expenses ORDER BY date DESC, id DESC")
    if df.empty:
        st.markdown(
            '<div class="empty-state"><div class="empty-icon">&#128203;</div>'
            '<h3>No transactions</h3>'
            '<p>Start adding expenses to build your records.</p></div>',
            unsafe_allow_html=True
        )
        st.stop()

    df["date"] = pd.to_datetime(df["date"])

    with st.expander("Filters and Search"):
        fc1, fc2, fc3, fc4 = st.columns(4)
        cats_f = ["All"] + sorted(df["category"].unique().tolist())
        pms_f  = ["All"] + sorted(df["payment_method"].dropna().unique().tolist())
        f_cat  = fc1.selectbox("Category", cats_f)
        f_pm   = fc2.selectbox("Payment",  pms_f)
        f_from = fc3.date_input("From", value=df["date"].min().date())
        f_to   = fc4.date_input("To",   value=df["date"].max().date())
        f_srch = st.text_input("Search description", placeholder="Type to search...")

        # ── Amount slider: guard against min == max (crash on Windows) ──
        _amin = float(df["amount"].min())
        _amax = float(df["amount"].max())
        if _amin < _amax:
            f_min, f_max = st.slider(
                "Amount range (Rs.)", _amin, _amax, (_amin, _amax)
            )
        else:
            f_min, f_max = _amin, _amax
            st.info(f"All transactions are Rs.{_amin:,.0f} — amount filter not applicable.")

    filt = df[
        (df["date"].dt.date >= f_from) &
        (df["date"].dt.date <= f_to) &
        (df["amount"] >= f_min) &
        (df["amount"] <= f_max)
    ]
    if f_cat != "All": filt = filt[filt["category"] == f_cat]
    if f_pm  != "All": filt = filt[filt["payment_method"] == f_pm]
    if f_srch:
        filt = filt[filt["desc"].str.contains(f_srch, case=False, na=False)]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Filtered Total", f"Rs. {filt['amount'].sum():,.0f}")
    c2.metric("Count",          str(len(filt)))
    c3.metric("Average",        f"Rs. {filt['amount'].mean():,.0f}" if not filt.empty else "—")
    c4.metric("Maximum",        f"Rs. {filt['amount'].max():,.0f}"  if not filt.empty else "—")

    st.markdown('<div class="sec-label">Results</div>', unsafe_allow_html=True)
    disp = filt[["id","date","category","amount","desc","payment_method","is_recurring"]].copy()
    disp["date"]         = disp["date"].dt.strftime("%d %b %Y")
    disp["amount"]       = disp["amount"].apply(lambda x: f"Rs.{x:,.0f}")
    disp["is_recurring"] = disp["is_recurring"].map({1: "Yes (Recurring)", 0: "No"})
    disp.columns = ["ID","Date","Category","Amount","Description","Payment","Recurring"]
    st.dataframe(disp, use_container_width=True, hide_index=True)

    col_exp, col_del = st.columns([1, 2])
    with col_exp:
        st.markdown(csv_download_link(filt), unsafe_allow_html=True)
    with col_del:
        with st.expander("Delete a Record"):
            if not filt.empty:
                del_id = st.number_input(
                    "Transaction ID to delete", step=1,
                    min_value=int(df["id"].min()),
                    max_value=int(df["id"].max())
                )
                if st.button("Delete"):
                    exe("DELETE FROM expenses WHERE id=?", (int(del_id),))
                    st.success(f"Record #{del_id} deleted.")
                    st.rerun()


# ═══════════════════════════════════════════════════
#  SETTINGS
# ═══════════════════════════════════════════════════
elif page == "Settings":
    st.markdown(
        '<div class="page-head"><div class="eyebrow">System</div>'
        '<h1>Settings</h1>'
        '<p>Manage your data and application preferences.</p></div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="sec-label">Data Management</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            '<div class="setting-block">'
            '<h4>Clear Expense History</h4>'
            '<p>Delete all transaction records. Budgets and goals are preserved.</p>'
            '</div>',
            unsafe_allow_html=True
        )
        if st.button("Clear Expenses", key="clr_e"):
            exe("DELETE FROM expenses")
            st.warning("All expense records deleted.")

        st.markdown(
            '<div class="setting-block">'
            '<h4>Clear All Budgets</h4>'
            '<p>Remove all budget limits across categories.</p>'
            '</div>',
            unsafe_allow_html=True
        )
        if st.button("Clear Budgets", key="clr_b"):
            exe("DELETE FROM budgets")
            st.warning("All budgets cleared.")

    with c2:
        st.markdown(
            '<div class="setting-block" style="border-color:rgba(251,113,133,0.2)">'
            '<h4>Factory Reset</h4>'
            '<p>Permanently delete all data: expenses, budgets, and savings goals.'
            ' This cannot be undone.</p>'
            '</div>',
            unsafe_allow_html=True
        )
        confirm = st.checkbox("I understand this is irreversible")
        if st.button("Factory Reset", key="factory"):
            if confirm:
                for t in ["expenses", "budgets", "goals"]:
                    exe(f"DELETE FROM {t}")
                st.error("All data wiped. Refresh to start fresh.")
            else:
                st.warning("Please check the confirmation box first.")

    st.markdown('<div class="sec-label">Database</div>', unsafe_allow_html=True)
    db_rows = {
        "Expenses":      sel("SELECT COUNT(*) as c FROM expenses")["c"][0],
        "Budgets":       sel("SELECT COUNT(*) as c FROM budgets")["c"][0],
        "Savings Goals": sel("SELECT COUNT(*) as c FROM goals")["c"][0],
    }
    for label, count in db_rows.items():
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:13px 0;border-bottom:1px solid var(--border);font-size:14px">
          <span style="color:var(--t2)">{label}</span>
          <span style="font-family:'Courier New',Consolas,monospace;font-weight:700;
                       color:var(--t1);background:var(--raised);
                       border:1px solid var(--border);padding:3px 12px;border-radius:99px">
            {count} records
          </span>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec-label">About</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:var(--raised);border:1px solid var(--border);
                border-radius:var(--r-lg);padding:22px 24px;">
      <div style="font-size:18px;font-weight:900;color:var(--t1);margin-bottom:6px">
        NexFin Pro
      </div>
      <div style="font-size:13px;color:var(--t2);line-height:1.8">
        Version 3.1-win &middot; Personal Finance Intelligence<br>
        Streamlit &middot; Plotly &middot; SQLite &middot; Python<br>
        <span style="color:var(--t3)">
          Data stored locally &middot; No cloud sync &middot; Privacy-first
        </span>
      </div>
      <div style="margin-top:14px;padding:10px 14px;background:var(--surface);
                  border:1px solid var(--border);border-radius:10px;
                  font-size:12px;color:var(--t3);word-break:break-all;">
        <span style="color:var(--t2);font-weight:600;">Database location:</span><br>
        <span style="font-family:'Courier New',Consolas,monospace;color:var(--blue)">
          {DB}
        </span>
      </div>
    </div>""", unsafe_allow_html=True)
