import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="PG Hyderabad",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,600;0,9..144,800;1,9..144,300&family=Epilogue:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] { font-family: 'Epilogue', sans-serif; }
#MainMenu, header, footer  { visibility: hidden; }
.block-container           { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none; }

:root {
    --cream:    #FAF7F2;
    --warm-50:  #FDF4EC;
    --terra:    #C7522A;
    --terra-d:  #9E3D18;
    --terra-l:  #E8866A;
    --slate:    #1C2430;
    --slate-m:  #2E3A4A;
    --slate-l:  #4A5568;
    --muted:    #8896A5;
    --border:   #E8E2D9;
    --success:  #2D7D5A;
    --warn:     #B45309;
    --green-bg: #F0FAF5;
    --green-bd: #A7D9C0;
    --amber-bg: #FFFBEB;
    --amber-bd: #FDE68A;
    --red-bg:   #FEF2F2;
    --red-bd:   #FECACA;
}

/* ── HERO ── */
.hero {
    background: var(--slate);
    padding: 2.8rem 3.5rem 2.4rem;
    position: relative; overflow: hidden;
}
.hero::before {
    content:''; position:absolute; inset:0;
    background: radial-gradient(ellipse 55% 90% at 92% 50%, rgba(199,82,42,.2) 0%, transparent 70%);
    pointer-events: none;
}
.hero-inner { max-width: 1200px; margin: 0 auto; position: relative; z-index: 1; }
.hero-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(199,82,42,.15); border: 1px solid rgba(199,82,42,.3);
    border-radius: 20px; padding: 4px 12px;
    font-size: 11px; font-weight: 600; color: var(--terra-l);
    margin-bottom: .9rem; letter-spacing: .04em;
}
.hero-h1 {
    font-family: 'Fraunces', serif;
    font-size: clamp(1.9rem, 4vw, 3rem);
    font-weight: 800; line-height: 1.1;
    color: #F8F4EF; margin-bottom: .6rem;
}
.hero-h1 em { font-style:italic; font-weight:300; color:var(--terra-l); }
.hero-sub {
    font-size:14px; font-weight:300;
    color:#8896A5; max-width:500px; line-height:1.7;
}
.hero-nums {
    display:flex; gap:2.5rem; margin-top:1.6rem;
}
.hero-num-val {
    font-family:'Fraunces',serif;
    font-size:2rem; font-weight:600; color:#F8F4EF; line-height:1;
}
.hero-num-lbl {
    font-size:10px; font-weight:600;
    letter-spacing:.1em; text-transform:uppercase;
    color:#4A5568; margin-top:2px;
}

/* ── FILTER STRIP ── */
.fstrip-wrap {
    background:#fff;
    border-bottom:1px solid var(--border);
    padding:.75rem 3.5rem;
    position:sticky; top:0; z-index:100;
    box-shadow: 0 2px 10px rgba(28,36,48,.05);
}

/* ── CONTENT ── */
.content { max-width:1200px; margin:0 auto; padding:2rem 3.5rem 4rem; }

/* ── STAT STRIP ── */
.stat-strip {
    display:grid; grid-template-columns:repeat(4,1fr);
    gap:1rem; margin-bottom:2rem;
}
.stat-card {
    background:#fff; border:1px solid var(--border);
    border-radius:14px; padding:1.1rem 1.3rem;
}
.stat-card.hi { border-left:3px solid var(--terra); }
.stat-lbl {
    font-size:10px; font-weight:600;
    letter-spacing:.1em; text-transform:uppercase;
    color:var(--muted); margin-bottom:6px;
}
.stat-val {
    font-family:'Fraunces',serif;
    font-size:1.65rem; font-weight:600;
    color:var(--slate); line-height:1;
}
.stat-sub { font-size:11px; color:var(--muted); margin-top:3px; }

/* ── SEC HEAD ── */
.sec-head {
    display:flex; align-items:baseline;
    justify-content:space-between; margin-bottom:1.1rem;
}
.sec-title {
    font-family:'Fraunces',serif;
    font-size:1.25rem; font-weight:600; color:var(--slate);
}
.sec-badge {
    font-size:11px; color:var(--muted);
    background:#F3F0EB; border-radius:20px; padding:2px 10px;
}

/* ── BEST BANNER ── */
.best-banner {
    background:linear-gradient(135deg,var(--slate) 0%,var(--slate-m) 100%);
    border-radius:18px; padding:1.4rem 1.8rem;
    margin-bottom:1.6rem; color:#fff;
    display:flex; align-items:center; gap:1.2rem; flex-wrap:wrap;
}
.bb-crown { font-size:2.2rem; flex-shrink:0; }
.bb-label {
    font-size:10px; font-weight:600;
    letter-spacing:.12em; text-transform:uppercase;
    color:var(--terra-l); margin-bottom:3px;
}
.bb-name {
    font-family:'Fraunces',serif;
    font-size:1.15rem; font-weight:600; color:#F8F4EF;
}
.bb-meta { font-size:12px; color:#8896A5; margin-top:2px; }
.bb-price {
    font-family:'Fraunces',serif;
    font-size:1.7rem; font-weight:600;
    color:var(--terra-l); margin-left:auto;
}
.bb-price span {
    font-family:'Epilogue',sans-serif;
    font-size:12px; font-weight:300; color:#4A5568;
}

/* ── PG CARD ── */
.pg-card {
    background:#fff; border:1px solid var(--border);
    border-radius:18px; padding:1.3rem 1.4rem;
    margin-bottom:.9rem; position:relative;
    transition:box-shadow .16s, border-color .16s, transform .16s;
}
.pg-card:hover {
    box-shadow:0 8px 28px rgba(28,36,48,.09);
    border-color:var(--terra-l); transform:translateY(-1px);
}
.pg-card.gold   { border-top:3px solid #F59E0B; }
.pg-card.silver { border-top:3px solid #94A3B8; }
.pg-card.bronze { border-top:3px solid #CD7C3A; }
.pg-rank { position:absolute; top:1rem; right:1rem; font-size:1.2rem; }
.pg-name {
    font-family:'Fraunces',serif;
    font-size:1rem; font-weight:600; color:var(--slate);
    margin-bottom:2px; padding-right:2rem;
}
.pg-loc { font-size:12px; color:var(--muted); margin-bottom:.7rem; }
.pg-price {
    font-family:'Fraunces',serif;
    font-size:1.45rem; font-weight:600; color:var(--terra); line-height:1;
    margin-bottom:.55rem;
}
.pg-price span { font-family:'Epilogue',sans-serif; font-size:12px; font-weight:400; color:var(--muted); }
.chips { display:flex; flex-wrap:wrap; gap:4px; margin-bottom:.55rem; }
.chip {
    font-size:11px; font-weight:500; border-radius:20px;
    padding:3px 9px; border:1px solid;
}
.cn { background:#F3F0EB; border-color:#E8E2D9; color:var(--slate-l); }
.cs { background:var(--amber-bg); border-color:var(--amber-bd); color:var(--warn); }
.cg { background:var(--green-bg); border-color:var(--green-bd); color:var(--success); }
.cr { background:var(--red-bg); border-color:var(--red-bd); color:#991B1B; }
.cb { background:#EFF6FF; border-color:#BFDBFE; color:#1D4ED8; }
.pg-quote {
    font-size:12px; font-style:italic; color:var(--muted);
    line-height:1.55; border-left:2px solid var(--border);
    padding-left:10px; margin-top:.55rem;
    display:-webkit-box; -webkit-line-clamp:2;
    -webkit-box-orient:vertical; overflow:hidden;
}

/* ── INSIGHT BOX ── */
.insight {
    background:var(--warm-50); border:1px solid #EDD9C8;
    border-radius:14px; padding:1rem 1.2rem; margin-top:1rem;
}
.insight-lbl {
    font-size:10px; font-weight:600;
    letter-spacing:.1em; text-transform:uppercase;
    color:var(--terra); margin-bottom:.5rem;
}
.irow {
    display:flex; justify-content:space-between;
    font-size:12px; padding:4px 0;
    border-bottom:1px solid #EDD9C8; color:var(--slate-l);
}
.irow:last-child { border-bottom:none; }
.ival { font-weight:600; color:var(--slate); font-family:'Fraunces',serif; }

/* ── CHART CARD ── */
.chart-title {
    font-family:'Fraunces',serif;
    font-size:1rem; font-weight:600; color:var(--slate); margin-bottom:2px;
}
.chart-sub { font-size:12px; color:var(--muted); margin-bottom:.6rem; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background:#F3F0EB; border-radius:12px;
    padding:4px; gap:3px; border:none;
}
.stTabs [data-baseweb="tab"] {
    border-radius:9px !important;
    font-family:'Epilogue',sans-serif !important;
    font-size:13px !important; font-weight:500 !important;
    color:var(--muted) !important; background:transparent !important;
    padding:6px 18px !important;
}
.stTabs [aria-selected="true"] {
    background:#fff !important; color:var(--slate) !important;
    box-shadow:0 1px 6px rgba(0,0,0,.08) !important;
}
.stTabs [data-baseweb="tab-border"] { display:none !important; }

/* ── BUTTONS ── */
.stButton button {
    background:var(--slate) !important; color:#F8F4EF !important;
    border:none !important; border-radius:10px !important;
    font-family:'Epilogue',sans-serif !important;
    font-size:12px !important; font-weight:500 !important;
    padding:6px 14px !important;
    transition:background .14s !important;
}
.stButton button:hover { background:var(--terra) !important; }
.stDownloadButton button {
    background:#fff !important; color:var(--slate) !important;
    border:1px solid var(--border) !important;
    border-radius:10px !important; width:100% !important;
    font-family:'Epilogue',sans-serif !important;
}

/* ── WIDGETS ── */
.stSelectbox > label, .stSlider > label, .stTextInput > label {
    font-size:11px !important; font-weight:600 !important;
    letter-spacing:.08em !important; text-transform:uppercase !important;
    color:var(--muted) !important;
}

/* ── EMPTY ── */
.empty {
    text-align:center; padding:3.5rem 2rem;
    background:#fff; border-radius:18px;
    border:1px dashed var(--border);
}
.empty-icon { font-size:2.8rem; margin-bottom:.7rem; }
.empty-title {
    font-family:'Fraunces',serif;
    font-size:1.1rem; font-weight:600; color:var(--slate);
}
.empty-sub { font-size:13px; color:var(--muted); margin-top:4px; }

/* ── FOOTER ── */
.footer {
    background:var(--slate); text-align:center;
    padding:1.4rem; font-size:12px; color:#4A5568;
}
.footer a { color:var(--terra-l); text-decoration:none; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  DATA
# ─────────────────────────────────────────────

COORDS = {
    "Gachibowli":    [17.4401, 78.3489],
    "Madhapur":      [17.4483, 78.3915],
    "Kondapur":      [17.4622, 78.3568],
    "Hitec City":    [17.4435, 78.3772],
    "Jubilee Hills": [17.4325, 78.4070],
    "Banjara Hills": [17.4123, 78.4389],
    "Kukatpally":    [17.4948, 78.3996],
    "Manikonda":     [17.4018, 78.3846],
    "Nanakramguda":  [17.4125, 78.3396],
    "Hafeezpet":     [17.4856, 78.3526],
    "Ameerpet":      [17.4375, 78.4483],
    "Unknown":       [17.3850, 78.4867],
}

TAG_RULES = [
    ("🍛 Great Food",     lambda t: any(x in t for x in ["good food","tasty","delicious","food is good"])),
    ("🚇 Metro Near",     lambda t: any(x in t for x in ["metro","transport","near bus","walking distance"])),
    ("✨ Very Clean",     lambda t: any(x in t for x in ["clean","neat","maintained","hygienic","tidy"])),
    ("🚀 Fast WiFi",      lambda t: any(x in t for x in ["wifi","internet","fast net","broadband"])),
    ("🔒 Secure",         lambda t: any(x in t for x in ["safe","security","cctv","gated","guard"])),
    ("🌿 Peaceful",       lambda t: any(x in t for x in ["quiet","peaceful","calm","no noise"])),
    ("❄️ AC Rooms",       lambda t: any(x in t for x in ["ac ","air condition","ac room","air-condition"])),
    ("🍽️ Mess Included",  lambda t: any(x in t for x in ["mess","meals included","food included","breakfast"])),
    ("🪳 Hygiene Issue",  lambda t: any(x in t for x in ["cockroach","bugs","dirty","unclean","pest"])),
    ("🥣 Bad Food",       lambda t: any(x in t for x in ["bad food","worst food","repetitive food","tasteless"])),
    ("🚫 No Parking",     lambda t: any(x in t for x in ["no parking","parking issue","congested"])),
    ("📶 Slow WiFi",      lambda t: any(x in t for x in ["slow wifi","no wifi","bad internet","no internet"])),
]
POS = {"🍛 Great Food","🚇 Metro Near","✨ Very Clean","🚀 Fast WiFi","🔒 Secure","🌿 Peaceful","❄️ AC Rooms","🍽️ Mess Included"}
NEG = {"🪳 Hygiene Issue","🥣 Bad Food","🚫 No Parking","📶 Slow WiFi"}

def generate_tags(text):
    t = str(text).lower()
    return [lbl for lbl, fn in TAG_RULES if fn(t)]

def clean_cost(x):
    if isinstance(x, str):
        s = x.replace("₹","").replace(",","").strip()
        if "-" in s:
            try:
                a, b = s.split("-", 1)
                return (float(a.strip()) + float(b.strip())) / 2
            except: return 0
        try: return float(s)
        except: return 0
    return float(x) if x else 0

CHART_COLORS = ["#C7522A","#2D7D5A","#1C2430","#B45309","#1D4ED8","#7C3AED","#0F766E","#BE185D","#0369A1","#065F46","#78350F"]

def base_layout(height=300):
    return dict(
        height=height, margin=dict(t=5,b=5,l=5,r=5),
        font=dict(family="Epilogue"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

def style_axes(fig):
    fig.update_xaxes(gridcolor="#F3F0EB", zerolinecolor="#F3F0EB")
    fig.update_yaxes(gridcolor="#F3F0EB", zerolinecolor="#F3F0EB")
    return fig

@st.cache_data(ttl=600)
def load_data():
    try:
        url = "https://docs.google.com/spreadsheets/d/1AW4EKm412u_UyYhf1swdhDsP5ikadr3XXeUTMrqvh4w/export?format=csv&gid=1856698473"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        df.rename(columns={
            "Name of PG/Hostel:":    "Name",
            "Type of PG":            "Type",
            "🌍 Location:":           "Location",
            "🏡Type of Sharing:":     "Sharing",
            "💰 Monthly Cost (₹):":   "Cost",
            "Overall Rating:":       "Rating",
            "Additional Comments:":  "Comments",
            "PG Owner Phone number": "Phone",
            "Contributor Gender":    "Gender",
        }, inplace=True)

        df["Cost"]    = df["Cost"].apply(clean_cost)
        df            = df[(df["Cost"] > 2000) & (df["Cost"] < 60000)]
        df["Rating"]  = pd.to_numeric(df["Rating"], errors="coerce").fillna(0)
        df["Location"]= df["Location"].fillna("Unknown").str.strip().str.title()
        df["Gender"]  = df["Gender"].fillna("Any").str.strip()
        df["Comments"]= df["Comments"].fillna("").str.strip()
        df["Name"]    = df["Name"].fillna("Unnamed PG").str.strip()
        df["Phone"]   = df["Phone"].fillna("").astype(str).str.strip()
        df["Sharing"] = df["Sharing"].fillna("Unknown").str.strip()

        df["Tags"]       = df["Comments"].apply(generate_tags)
        df["PosTags"]    = df["Tags"].apply(lambda ts: [t for t in ts if t in POS])
        df["NegTags"]    = df["Tags"].apply(lambda ts: [t for t in ts if t in NEG])
        coords           = df["Location"].map(lambda x: COORDS.get(x, COORDS["Unknown"]))
        df["lat"]        = coords.map(lambda x: x[0])
        df["lon"]        = coords.map(lambda x: x[1])
        df["ValueScore"] = ((df["Rating"] ** 2) / df["Cost"].replace(0, np.nan)) * 5000
        df["ValueScore"] = df["ValueScore"].fillna(0)
        return df
    except Exception as e:
        st.error(f"Could not load data: {e}")
        return None

df = load_data()
if df is None:
    st.stop()

# ─────────────────────────────────────────────
#  HERO
# ─────────────────────────────────────────────
total_pgs   = len(df)
total_areas = df["Location"].nunique()

st.markdown(f"""
<div class="hero">
  <div class="hero-inner">
    <div style="display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:1.5rem;">
      <div>
        <span class="hero-badge">🏙️ Hyderabad · community-powered</span>
        <h1 class="hero-h1">Find your next<br><em>home away from home</em></h1>
        <p class="hero-sub">Real PG reviews from the Reddit Hyderabad community — unfiltered prices, honest ratings, direct contacts.</p>
        <div class="hero-nums">
          <div>
            <div class="hero-num-val">{total_pgs}</div>
            <div class="hero-num-lbl">PG Listings</div>
          </div>
          <div>
            <div class="hero-num-val" style="color:var(--terra-l);">{total_areas}</div>
            <div class="hero-num-lbl">Areas Covered</div>
          </div>
          <div>
            <div class="hero-num-val">{df[df['Rating']>0]['Rating'].mean():.1f}⭐</div>
            <div class="hero-num-lbl">Avg Rating</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FILTER BAR
# ─────────────────────────────────────────────
st.markdown('<div class="fstrip-wrap">', unsafe_allow_html=True)
fc1, fc2, fc3, fc4, fc5 = st.columns([2, 2, 2, 3, 2])

with fc1:
    sel_loc = st.selectbox("📍 Area", ["All Areas"] + sorted(df["Location"].unique().tolist()))
with fc2:
    sel_gender = st.selectbox("🚻 Gender Preference", ["Any"] + sorted(df["Gender"].unique().tolist()))
with fc3:
    sel_share = st.selectbox("🏠 Room Type", ["Any"] + sorted(df["Sharing"].dropna().unique().tolist()))
with fc4:
    budget = st.slider("💰 Max Budget", int(df["Cost"].min()), int(df["Cost"].max()), 25000, 500, format="₹%d")
with fc5:
    min_rat = st.slider("⭐ Min Rating", 0.0, 5.0, 0.0, 0.5)

st.markdown("</div>", unsafe_allow_html=True)

# ── global search bar ──
st.markdown("""
<style>
.gsearch-wrap {
    background:#FAF7F2; border-bottom:1px solid #E8E2D9;
    padding:.65rem 3.5rem;
}
.gsearch-wrap .stTextInput input {
    border-radius:30px !important;
    font-size:14px !important;
    border-color:#E8E2D9 !important;
    background:#fff !important;
}
.gsearch-wrap .stTextInput input:focus {
    border-color:#C7522A !important;
    box-shadow:0 0 0 3px rgba(199,82,42,.12) !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="gsearch-wrap">', unsafe_allow_html=True)
gs_col, gs_info = st.columns([4, 1])
with gs_col:
    global_search = st.text_input(
        "global_search_hidden",
        placeholder="🔍  Search across all PGs — try 'AC', 'metro', 'Gachibowli', 'clean', 'parking'…",
        label_visibility="collapsed",
        key="global_search",
    )
with gs_info:
    st.markdown("""
    <div style="padding-top:.4rem;font-size:11px;color:#8896A5;line-height:1.6;">
      Searches name, area,<br>reviews &amp; tags
    </div>""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FILTER LOGIC  (dropdowns + sliders + global search)
# ─────────────────────────────────────────────
fdf = df.copy()
if sel_loc    != "All Areas": fdf = fdf[fdf["Location"] == sel_loc]
if sel_gender != "Any":       fdf = fdf[fdf["Gender"]   == sel_gender]
if sel_share  != "Any":       fdf = fdf[fdf["Sharing"]  == sel_share]
fdf = fdf[fdf["Cost"]   <= budget]
fdf = fdf[fdf["Rating"] >= min_rat]

# global keyword search — hits name, location, comments, sharing, gender, and tags
if global_search.strip():
    q = global_search.strip()
    tag_match  = fdf["Tags"].apply(lambda ts: any(q.lower() in t.lower() for t in ts))
    text_mask  = (
        fdf["Name"].str.contains(q, case=False, na=False)     |
        fdf["Location"].str.contains(q, case=False, na=False) |
        fdf["Comments"].str.contains(q, case=False, na=False) |
        fdf["Sharing"].str.contains(q, case=False, na=False)  |
        fdf["Gender"].str.contains(q, case=False, na=False)   |
        tag_match
    )
    fdf = fdf[text_mask]

fdf = fdf.sort_values("ValueScore", ascending=False).reset_index(drop=True)

# ─────────────────────────────────────────────
#  CONTENT
# ─────────────────────────────────────────────
st.markdown('<div class="content">', unsafe_allow_html=True)

# ── stat strip ──
avg_cost = int(fdf["Cost"].mean()) if not fdf.empty else 0
avg_rat  = fdf["Rating"].mean()    if not fdf.empty else 0
try:    cheap_area = fdf.groupby("Location")["Cost"].mean().idxmin()
except: cheap_area = "—"
try:    best_area  = fdf[fdf["Rating"] > 0].groupby("Location")["Rating"].mean().idxmax()
except: best_area  = "—"

st.markdown(f"""
<div class="stat-strip">
  <div class="stat-card hi">
    <div class="stat-lbl">PGs Found</div>
    <div class="stat-val">{len(fdf)}</div>
    <div class="stat-sub">of {total_pgs} total</div>
  </div>
  <div class="stat-card">
    <div class="stat-lbl">Avg Monthly Rent</div>
    <div class="stat-val">₹{avg_cost:,}</div>
    <div class="stat-sub">for current filters</div>
  </div>
  <div class="stat-card">
    <div class="stat-lbl">Avg Rating</div>
    <div class="stat-val">{avg_rat:.1f} ⭐</div>
    <div class="stat-sub">community score</div>
  </div>
  <div class="stat-card">
    <div class="stat-lbl">Most Affordable Area</div>
    <div class="stat-val" style="font-size:1.15rem;">{cheap_area}</div>
    <div class="stat-sub">by average rent</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────
t1, t2, t3, t4 = st.tabs(["🏆  Top Picks", "📊  Market Insights", "🗺️  Map View", "📋  Full Directory"])

# ══════════════════════════════════════════════
#  TAB 1 — TOP PICKS
# ══════════════════════════════════════════════
with t1:
    if fdf.empty:
        st.markdown("""
        <div class="empty">
          <div class="empty-icon">🔍</div>
          <div class="empty-title">No PGs match your filters</div>
          <div class="empty-sub">Try raising your budget or removing a filter.</div>
        </div>""", unsafe_allow_html=True)
    else:
        best = fdf.iloc[0]
        st.markdown(f"""
        <div class="best-banner">
          <div class="bb-crown">🏅</div>
          <div>
            <div class="bb-label">Best Value Pick</div>
            <div class="bb-name">{best['Name']}</div>
            <div class="bb-meta">📍 {best['Location']} &nbsp;·&nbsp; ⭐ {best['Rating']:.1f} &nbsp;·&nbsp; {best['Sharing']}</div>
          </div>
          <div class="bb-price">₹{int(best['Cost']):,}<span>/mo</span></div>
        </div>
        """, unsafe_allow_html=True)

        left, right = st.columns([1, 1], gap="large")

        # ── Card list ──
        with left:
            show_n  = min(10, len(fdf))
            ranks   = ["🥇","🥈","🥉"] + [f"#{i+1}" for i in range(3, show_n)]
            classes = ["gold","silver","bronze"] + [""]*max(0, show_n-3)

            st.markdown(f"""
            <div class="sec-head">
              <span class="sec-title">Top {show_n} PGs</span>
              <span class="sec-badge">{len(fdf)} matching</span>
            </div>""", unsafe_allow_html=True)

            for i in range(show_n):
                row = fdf.iloc[i]
                chips = (f'<span class="chip cs">⭐ {row["Rating"]:.1f}</span>'
                         f'<span class="chip cn">{row["Sharing"]}</span>'
                         f'<span class="chip cb">{row["Gender"]}</span>')
                pos_chips = "".join(f'<span class="chip cg">{t}</span>' for t in row["PosTags"][:4])
                neg_chips = "".join(f'<span class="chip cr">{t}</span>' for t in row["NegTags"][:2])
                tag_row   = f'<div class="chips">{pos_chips}{neg_chips}</div>' if pos_chips or neg_chips else ""
                quote     = f'<div class="pg-quote">"{row["Comments"][:130]}"</div>' if row["Comments"] else ""

                st.markdown(f"""
                <div class="pg-card {classes[i]}">
                  <span class="pg-rank">{ranks[i]}</span>
                  <div class="pg-name">{row['Name']}</div>
                  <div class="pg-loc">📍 {row['Location']}</div>
                  <div class="chips">{chips}</div>
                  {tag_row}
                  <div class="pg-price">₹{int(row['Cost']):,} <span>/month</span></div>
                  {quote}
                </div>""", unsafe_allow_html=True)

                ca, cb = st.columns(2)
                with ca:
                    if st.button("📞 Show Contact", key=f"ph_{i}"):
                        ph = str(row["Phone"]).strip()
                        if ph and ph not in ["nan", ""]:
                            st.success(f"📱 {ph}")
                        else:
                            st.info("No contact listed for this PG.")
                with cb:
                    if st.button("📋 Copy Details", key=f"cp_{i}"):
                        st.code(f"{row['Name']} | {row['Location']} | ₹{int(row['Cost']):,}/mo | ⭐{row['Rating']:.1f} | {row['Phone']}")

        # ── Right panel: chart + area table ──
        with right:
            st.markdown("""
            <div class="sec-head">
              <span class="sec-title">Value Matrix</span>
            </div>
            <p style="font-size:13px;color:#8896A5;margin-bottom:.7rem;">
              Top-left corner = best deal. Bubble size = value score.
            </p>""", unsafe_allow_html=True)

            top20 = fdf.head(20)
            fig = px.scatter(
                top20, x="Cost", y="Rating",
                size="ValueScore", color="Location",
                hover_name="Name",
                hover_data={"Sharing":True,"Cost":":₹,.0f","Rating":True,"ValueScore":False},
                size_max=55,
                color_discrete_sequence=CHART_COLORS,
                template="simple_white",
            )
            fig.add_hline(y=4.0, line_dash="dot", line_color="#2D7D5A",
                          annotation_text="Quality bar (4★)", annotation_font_color="#2D7D5A")
            fig.update_layout(
                **base_layout(360),
                legend=dict(orientation="h", y=-0.14, x=0, font_size=10),
                xaxis_title="Monthly Rent (₹)", yaxis_title="Rating",
            )
            fig.update_yaxes(range=[0, 5.5])
            fig.update_traces(marker=dict(opacity=0.85, line=dict(width=1.5, color="white")))
            style_axes(fig)
            st.plotly_chart(fig, use_container_width=True)

            # area summary
            area_stats = (fdf.groupby("Location")
                          .agg(avg_rent=("Cost","mean"), avg_rating=("Rating","mean"), count=("Name","count"))
                          .sort_values("avg_rent"))
            rows_html = "".join(f"""
            <div class="irow">
              <span>📍 {area} <span style="color:#8896A5;font-size:11px;">({int(row['count'])} PGs)</span></span>
              <span class="ival">₹{int(row['avg_rent']):,} · {row['avg_rating']:.1f}⭐</span>
            </div>""" for area, row in area_stats.iterrows())
            st.markdown(f"""
            <div class="insight">
              <div class="insight-lbl">Area Summary — cheapest first</div>
              {rows_html}
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  TAB 2 — MARKET INSIGHTS
# ══════════════════════════════════════════════
with t2:
    if fdf.empty:
        st.info("No data for current filters.")
    else:
        r1, r2 = st.columns([3, 2], gap="large")
        with r1:
            st.markdown('<div class="chart-title">Rent Range by Area</div><div class="chart-sub">Each dot is a PG. Box = median & spread.</div>', unsafe_allow_html=True)
            fig_box = px.box(fdf, x="Location", y="Cost", color="Location",
                             points="all", hover_data=["Name","Rating"],
                             template="simple_white",
                             color_discrete_sequence=CHART_COLORS)
            fig_box.update_layout(**base_layout(300), showlegend=False,
                                  xaxis_title="", yaxis_title="Monthly Rent (₹)")
            style_axes(fig_box)
            st.plotly_chart(fig_box, use_container_width=True)

        with r2:
            st.markdown('<div class="chart-title">Room Type Share</div><div class="chart-sub">Market split by sharing preference.</div>', unsafe_allow_html=True)
            fig_pie = px.pie(fdf, names="Sharing", hole=0.55,
                             color_discrete_sequence=["#1C2430","#C7522A","#2D7D5A","#B45309","#1D4ED8","#7C3AED"],
                             template="simple_white")
            fig_pie.update_traces(textposition="outside", textinfo="label+percent", textfont_size=11)
            fig_pie.update_layout(**base_layout(300), showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)

        r3, r4 = st.columns(2, gap="large")
        with r3:
            st.markdown('<div class="chart-title">Avg Rent by Area</div><div class="chart-sub">Sorted cheapest → priciest.</div>', unsafe_allow_html=True)
            aa = fdf.groupby("Location")["Cost"].mean().sort_values().reset_index()
            fig_bar = px.bar(aa, x="Cost", y="Location", orientation="h",
                             template="simple_white", color="Cost",
                             color_continuous_scale=["#FDF4EC","#C7522A"],
                             text=aa["Cost"].apply(lambda x: f"₹{int(x):,}"))
            fig_bar.update_layout(**base_layout(280), coloraxis_showscale=False,
                                  showlegend=False, xaxis_title="Avg Rent (₹)", yaxis_title="")
            fig_bar.update_traces(textposition="outside")
            style_axes(fig_bar)
            st.plotly_chart(fig_bar, use_container_width=True)

        with r4:
            st.markdown('<div class="chart-title">Ratings Distribution</div><div class="chart-sub">How PGs are rated overall.</div>', unsafe_allow_html=True)
            fig_hist = px.histogram(fdf[fdf["Rating"] > 0], x="Rating", nbins=10,
                                    template="simple_white",
                                    color_discrete_sequence=["#C7522A"])
            fig_hist.update_layout(**base_layout(280), bargap=0.1,
                                   xaxis_title="Rating", yaxis_title="No. of PGs")
            style_axes(fig_hist)
            st.plotly_chart(fig_hist, use_container_width=True)

        r5, r6 = st.columns(2, gap="large")
        with r5:
            st.markdown('<div class="chart-title">Does Paying More Mean Better?</div><div class="chart-sub">Cost vs rating with trend line.</div>', unsafe_allow_html=True)
            fig_sc = px.scatter(fdf[fdf["Rating"] > 0], x="Cost", y="Rating",
                                color="Sharing", hover_name="Name",
                                opacity=0.65,
                                template="simple_white",
                                color_discrete_sequence=["#C7522A","#2D7D5A","#1C2430","#B45309"])
            fig_sc.update_layout(**base_layout(260),
                                 legend=dict(orientation="h", y=-0.2, font_size=11),
                                 xaxis_title="Monthly Rent (₹)", yaxis_title="Rating")
            style_axes(fig_sc)
            st.plotly_chart(fig_sc, use_container_width=True)

        with r6:
            st.markdown('<div class="chart-title">Gender Preference Mix</div><div class="chart-sub">Availability across gender categories.</div>', unsafe_allow_html=True)
            gc = fdf["Gender"].value_counts().reset_index()
            gc.columns = ["Gender","Count"]
            fig_gen = px.bar(gc, x="Gender", y="Count", template="simple_white",
                             color="Gender",
                             color_discrete_sequence=["#C7522A","#2D7D5A","#1C2430","#B45309","#7C3AED"])
            fig_gen.update_layout(**base_layout(260), showlegend=False,
                                  xaxis_title="", yaxis_title="No. of PGs")
            style_axes(fig_gen)
            st.plotly_chart(fig_gen, use_container_width=True)

# ══════════════════════════════════════════════
#  TAB 3 — MAP
# ══════════════════════════════════════════════
with t3:
    if fdf.empty:
        st.info("No PGs to display on map.")
    else:
        st.markdown("""
        <div style="background:#FFFBEB;border:1px solid #FDE68A;border-radius:12px;
             padding:.65rem 1rem;margin-bottom:1rem;font-size:13px;color:#92400E;">
          📌 <strong>Note:</strong> Pins are placed at area centre points, not exact addresses.
          Call the owner for precise location.
        </div>""", unsafe_allow_html=True)

        map_df = fdf[["lat","lon","Name","Location","Cost","Rating","Sharing"]].copy()
        map_df["lat"] += np.random.normal(0, 0.0025, len(map_df))
        map_df["lon"] += np.random.normal(0, 0.0025, len(map_df))

        fig_map = px.scatter_mapbox(
            map_df, lat="lat", lon="lon",
            hover_name="Name",
            hover_data={"Location":True,"Cost":":₹,.0f","Rating":True,
                        "Sharing":True,"lat":False,"lon":False},
            color="Rating", size=[12]*len(map_df),
            color_continuous_scale=["#E11D48","#F59E0B","#2D7D5A"],
            range_color=[0, 5], zoom=11, height=560,
        )
        fig_map.update_layout(
            mapbox_style="carto-positron",
            margin=dict(t=0,b=0,l=0,r=0),
            coloraxis_colorbar=dict(title="Rating", len=0.45, thickness=12,
                                    tickfont=dict(family="Epilogue", size=11)),
            font=dict(family="Epilogue"),
        )
        st.plotly_chart(fig_map, use_container_width=True)

# ══════════════════════════════════════════════
#  TAB 4 — FULL DIRECTORY
# ══════════════════════════════════════════════
with t4:
    if fdf.empty:
        st.markdown("""
        <div class="empty">
          <div class="empty-icon">📋</div>
          <div class="empty-title">No results found</div>
          <div class="empty-sub">Adjust the filters above to see listings.</div>
        </div>""", unsafe_allow_html=True)
    else:
        search = st.text_input("🔍 Search by name, area or keyword",
                               placeholder="e.g. Gachibowli, clean, AC, WiFi, metro…")
        show_df = fdf.copy()
        if search.strip():
            mask = (
                show_df["Name"].str.contains(search, case=False, na=False) |
                show_df["Location"].str.contains(search, case=False, na=False) |
                show_df["Comments"].str.contains(search, case=False, na=False)
            )
            show_df = show_df[mask]
            st.caption(f'Showing {len(show_df)} results for "{search}"')

        cols = ["Name","Location","Sharing","Gender","Cost","Rating","Phone","Comments"]
        st.dataframe(
            show_df[cols],
            column_config={
                "Name":     st.column_config.TextColumn("PG Name",   width="medium"),
                "Cost":     st.column_config.NumberColumn("Rent/mo", format="₹%d"),
                "Rating":   st.column_config.ProgressColumn("Rating",min_value=0, max_value=5, format="%.1f ⭐"),
                "Comments": st.column_config.TextColumn("Reviews",   width="large"),
                "Phone":    st.column_config.TextColumn("Contact",   width="small"),
            },
            hide_index=True, use_container_width=True, height=520,
        )

        csv = show_df[cols].to_csv(index=False).encode("utf-8")
        st.download_button("📥 Export as CSV", data=csv,
                           file_name="hyd_pg_list.csv", mime="text/csv",
                           use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div class="footer">
  Community data from <strong style="color:#8896A5;">Reddit r/hyderabad</strong>
  &nbsp;·&nbsp; Built with Python & Streamlit
  &nbsp;·&nbsp; <a href="https://github.com/prosuvinhere/Hyd_PG">⭐ Star on GitHub</a>
</div>
""", unsafe_allow_html=True)
