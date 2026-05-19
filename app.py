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
#  GLOBAL CSS  — DARK MODE
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background: #0A0C10 !important;
    color: #C8D0DC !important;
}
#MainMenu, header, footer  { visibility: hidden; }
.block-container           { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none; }

/* Force Streamlit background dark */
.stApp, .main, [data-testid="stAppViewContainer"] {
    background: #0A0C10 !important;
}
[data-testid="stHeader"] { background: transparent !important; }

:root {
    /* Dark backgrounds */
    --bg-base:    #0A0C10;
    --bg-1:       #0F1117;
    --bg-2:       #141720;
    --bg-3:       #1A1F2E;
    --bg-card:    #13161F;
    --bg-hover:   #1C2030;

    /* Borders */
    --border:     #1E2335;
    --border-m:   #252A3D;
    --border-l:   #2E3450;

    /* Brand — electric amber/orange */
    --accent:     #F5A623;
    --accent-d:   #C7821A;
    --accent-l:   #FFD580;
    --accent-dim: rgba(245,166,35,.12);
    --accent-glow:rgba(245,166,35,.25);

    /* Teal accent */
    --teal:       #00C9A7;
    --teal-dim:   rgba(0,201,167,.1);
    --teal-bd:    rgba(0,201,167,.25);

    /* Text */
    --text-1:     #EDF0F7;
    --text-2:     #9AA3B5;
    --text-3:     #5C6478;

    /* Semantic */
    --success:    #00C9A7;
    --warn:       #F5A623;
    --danger:     #F0546B;
    --info:       #5B8CF5;

    /* Status chip bgs */
    --chip-n-bg:  rgba(92,100,120,.15);
    --chip-n-bd:  #252A3D;
    --chip-g-bg:  rgba(0,201,167,.1);
    --chip-g-bd:  rgba(0,201,167,.3);
    --chip-r-bg:  rgba(240,84,107,.1);
    --chip-r-bd:  rgba(240,84,107,.3);
    --chip-b-bg:  rgba(91,140,245,.1);
    --chip-b-bd:  rgba(91,140,245,.3);
    --chip-y-bg:  rgba(245,166,35,.1);
    --chip-y-bd:  rgba(245,166,35,.3);
}

/* ── HERO ── */
.hero {
    background: var(--bg-1);
    padding: 3rem 3.5rem 2.6rem;
    position: relative; overflow: hidden;
    border-bottom: 1px solid var(--border);
}
.hero::before {
    content:''; position:absolute; top:-60px; right:-80px;
    width:600px; height:600px;
    background: radial-gradient(circle, rgba(245,166,35,.08) 0%, transparent 65%);
    pointer-events: none;
}
.hero::after {
    content:''; position:absolute; bottom:-80px; left:200px;
    width:400px; height:400px;
    background: radial-gradient(circle, rgba(0,201,167,.05) 0%, transparent 65%);
    pointer-events: none;
}
.hero-inner { max-width: 1200px; margin: 0 auto; position: relative; z-index: 1; }
.hero-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--accent-dim); border: 1px solid var(--accent-glow);
    border-radius: 20px; padding: 4px 13px;
    font-size: 11px; font-weight: 600; color: var(--accent);
    margin-bottom: 1rem; letter-spacing: .05em; text-transform: uppercase;
}
.hero-h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2rem, 4vw, 3.2rem);
    font-weight: 800; line-height: 1.08;
    color: var(--text-1); margin-bottom: .7rem;
}
.hero-h1 em {
    font-style: italic; font-weight: 400;
    color: var(--accent);
    background: linear-gradient(90deg, var(--accent), var(--teal));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-size: 14px; font-weight: 300;
    color: var(--text-2); max-width: 480px; line-height: 1.8;
}
.hero-nums {
    display: flex; gap: 3rem; margin-top: 2rem;
}
.hero-num-val {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem; font-weight: 700; color: var(--text-1); line-height: 1;
}
.hero-num-val.accent { color: var(--accent); }
.hero-num-lbl {
    font-size: 10px; font-weight: 600;
    letter-spacing: .1em; text-transform: uppercase;
    color: var(--text-3); margin-top: 4px;
}
.hero-divider { width: 1px; background: var(--border); align-self: stretch; }

/* Force Streamlit widgets dark */
.stSelectbox > div > div,
.stTextInput > div > div > input {
    background: var(--bg-3) !important;
    border-color: var(--border-m) !important;
    color: var(--text-1) !important;
    border-radius: 10px !important;
}
.stSelectbox > div > div:hover,
.stTextInput > div > div > input:hover {
    border-color: var(--border-l) !important;
}
.stSelectbox > div > div:focus-within,
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-dim) !important;
}
/* Dropdown options */
[data-baseweb="popover"] { background: var(--bg-3) !important; }
[data-baseweb="menu"] { background: var(--bg-3) !important; }
[role="option"] { background: var(--bg-3) !important; color: var(--text-1) !important; }
[role="option"]:hover { background: var(--bg-hover) !important; }

/* Slider */
[data-testid="stSlider"] .rc-slider-track { background: var(--accent) !important; }
[data-testid="stSlider"] .rc-slider-handle {
    border-color: var(--accent) !important;
    background: var(--accent) !important;
    box-shadow: 0 0 8px var(--accent-glow) !important;
}
[data-testid="stSlider"] .rc-slider-rail { background: var(--border-l) !important; }
div[data-testid="stSlider"] p { color: var(--text-2) !important; }

/* ── CONTENT ── */
.content { max-width: 1200px; margin: 0 auto; padding: 2rem 3.5rem 4rem; }

/* ── STAT STRIP ── */
.stat-strip {
    display: grid; grid-template-columns: repeat(4,1fr);
    gap: 1rem; margin-bottom: 2rem;
}
.stat-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px; padding: 1.2rem 1.4rem;
    position: relative; overflow: hidden;
    transition: border-color .2s, transform .2s;
}
.stat-card:hover { border-color: var(--border-l); transform: translateY(-2px); }
.stat-card.hi {
    border-left: 3px solid var(--accent);
    background: linear-gradient(135deg, rgba(245,166,35,.06) 0%, var(--bg-card) 60%);
}
.stat-lbl {
    font-size: 10px; font-weight: 600;
    letter-spacing: .12em; text-transform: uppercase;
    color: var(--text-3); margin-bottom: 8px;
}
.stat-val {
    font-family: 'Syne', sans-serif;
    font-size: 1.75rem; font-weight: 700;
    color: var(--text-1); line-height: 1;
}
.stat-sub { font-size: 11px; color: var(--text-3); margin-top: 5px; }

/* ── SEC HEAD ── */
.sec-head {
    display: flex; align-items: baseline;
    justify-content: space-between; margin-bottom: 1.1rem;
}
.sec-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.2rem; font-weight: 700; color: var(--text-1);
}
.sec-badge {
    font-size: 11px; color: var(--text-3);
    background: var(--bg-3); border: 1px solid var(--border);
    border-radius: 20px; padding: 2px 10px;
}

/* ── BEST BANNER ── */
.best-banner {
    background: linear-gradient(135deg, var(--bg-2) 0%, var(--bg-3) 100%);
    border: 1px solid var(--border-m);
    border-radius: 20px; padding: 1.5rem 1.8rem;
    margin-bottom: 1.6rem;
    display: flex; align-items: center; gap: 1.4rem; flex-wrap: wrap;
    position: relative; overflow: hidden;
}
.best-banner::before {
    content: ''; position: absolute; top: -30px; right: -30px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(245,166,35,.1) 0%, transparent 70%);
    pointer-events: none;
}
.bb-crown { font-size: 2.5rem; flex-shrink: 0; filter: drop-shadow(0 0 12px rgba(245,166,35,.5)); }
.bb-label {
    font-size: 10px; font-weight: 600;
    letter-spacing: .12em; text-transform: uppercase;
    color: var(--accent); margin-bottom: 4px;
}
.bb-name {
    font-family: 'Syne', sans-serif;
    font-size: 1.2rem; font-weight: 700; color: var(--text-1);
}
.bb-meta { font-size: 12px; color: var(--text-2); margin-top: 3px; }
.bb-price {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem; font-weight: 700;
    color: var(--accent); margin-left: auto;
}
.bb-price span {
    font-family: 'DM Sans', sans-serif;
    font-size: 12px; font-weight: 300; color: var(--text-3);
}

/* ── PG CARD ── */
.pg-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 18px; padding: 1.3rem 1.5rem;
    margin-bottom: .85rem; position: relative;
    transition: box-shadow .2s, border-color .2s, transform .2s;
}
.pg-card:hover {
    box-shadow: 0 8px 32px rgba(0,0,0,.5), 0 0 0 1px var(--border-l);
    transform: translateY(-2px);
}
.pg-card.gold   { border-top: 3px solid var(--accent); }
.pg-card.silver { border-top: 3px solid #7C8FA6; }
.pg-card.bronze { border-top: 3px solid #A67C52; }
.pg-rank { position: absolute; top: 1rem; right: 1rem; font-size: 1.3rem; }
.pg-name {
    font-family: 'Syne', sans-serif;
    font-size: 1rem; font-weight: 600; color: var(--text-1);
    margin-bottom: 3px; padding-right: 2.5rem;
}
.pg-loc { font-size: 12px; color: var(--text-3); margin-bottom: .8rem; }
.pg-price {
    font-family: 'Syne', sans-serif;
    font-size: 1.5rem; font-weight: 700; color: var(--accent); line-height: 1;
    margin-bottom: .6rem;
}
.pg-price span { font-family: 'DM Sans', sans-serif; font-size: 12px; font-weight: 400; color: var(--text-3); }
.chips { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: .6rem; }
.chip {
    font-size: 11px; font-weight: 500; border-radius: 20px;
    padding: 3px 10px; border: 1px solid;
}
.cn { background: var(--chip-n-bg); border-color: var(--chip-n-bd); color: var(--text-2); }
.cs { background: var(--chip-y-bg); border-color: var(--chip-y-bd); color: var(--accent); }
.cg { background: var(--chip-g-bg); border-color: var(--chip-g-bd); color: var(--teal); }
.cr { background: var(--chip-r-bg); border-color: var(--chip-r-bd); color: var(--danger); }
.cb { background: var(--chip-b-bg); border-color: var(--chip-b-bd); color: var(--info); }
.pg-quote {
    font-size: 12px; font-style: italic; color: var(--text-3);
    line-height: 1.6; border-left: 2px solid var(--border-l);
    padding-left: 12px; margin-top: .6rem;
    display: -webkit-box; -webkit-line-clamp: 2;
    -webkit-box-orient: vertical; overflow: hidden;
}

/* ── INSIGHT BOX ── */
.insight {
    background: var(--bg-2); border: 1px solid var(--border-m);
    border-radius: 16px; padding: 1.1rem 1.3rem; margin-top: 1rem;
}
.insight-lbl {
    font-size: 10px; font-weight: 600;
    letter-spacing: .12em; text-transform: uppercase;
    color: var(--accent); margin-bottom: .6rem;
}
.irow {
    display: flex; justify-content: space-between;
    font-size: 12px; padding: 5px 0;
    border-bottom: 1px solid var(--border); color: var(--text-2);
}
.irow:last-child { border-bottom: none; }
.ival { font-weight: 600; color: var(--text-1); font-family: 'Syne', sans-serif; font-size: 13px; }

/* ── CHART CARD ── */
.chart-title {
    font-family: 'Syne', sans-serif;
    font-size: 1rem; font-weight: 700; color: var(--text-1); margin-bottom: 2px;
}
.chart-sub { font-size: 12px; color: var(--text-3); margin-bottom: .7rem; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-2); border-radius: 14px;
    padding: 5px; gap: 3px; border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important; font-weight: 500 !important;
    color: var(--text-3) !important; background: transparent !important;
    padding: 7px 20px !important;
}
.stTabs [aria-selected="true"] {
    background: var(--bg-3) !important; color: var(--text-1) !important;
    box-shadow: 0 2px 10px rgba(0,0,0,.4) !important;
    border: 1px solid var(--border-m) !important;
}
.stTabs [data-baseweb="tab-border"] { display: none !important; }
[data-testid="stTabsContent"] { background: transparent !important; }

/* ── BUTTONS ── */
.stButton button {
    background: var(--bg-3) !important;
    color: var(--text-1) !important;
    border: 1px solid var(--border-m) !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 12px !important; font-weight: 500 !important;
    padding: 6px 14px !important;
    transition: all .15s !important;
}
.stButton button:hover {
    background: var(--accent-dim) !important;
    border-color: var(--accent-glow) !important;
    color: var(--accent) !important;
}
.stDownloadButton button {
    background: var(--bg-3) !important;
    color: var(--text-1) !important;
    border: 1px solid var(--border-m) !important;
    border-radius: 10px !important; width: 100% !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stDownloadButton button:hover {
    border-color: var(--teal-bd) !important;
    color: var(--teal) !important;
}

/* ── WIDGETS LABELS ── */
.stSelectbox > label, .stSlider > label, .stTextInput > label {
    font-size: 11px !important; font-weight: 600 !important;
    letter-spacing: .08em !important; text-transform: uppercase !important;
    color: var(--text-3) !important;
}
.stSelectbox [data-baseweb="select"] span { color: var(--text-1) !important; }

/* Dataframe dark */
.stDataFrame, [data-testid="stDataFrame"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
}
[data-testid="stDataFrame"] th {
    background: var(--bg-2) !important;
    color: var(--text-2) !important;
    border-color: var(--border) !important;
}
[data-testid="stDataFrame"] td {
    color: var(--text-1) !important;
    border-color: var(--border) !important;
}

/* ── SEARCH BAR ── */
.gsearch-wrap {
    background: var(--bg-1);
    border-bottom: 1px solid var(--border);
    padding: .7rem 3.5rem;
}
.gsearch-wrap .stTextInput input {
    border-radius: 30px !important;
    font-size: 14px !important;
    border-color: var(--border-m) !important;
    background: var(--bg-3) !important;
    color: var(--text-1) !important;
}
.gsearch-wrap .stTextInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-dim) !important;
}
.gsearch-wrap .stTextInput input::placeholder { color: var(--text-3) !important; }

/* ── ALERTS / INFO ── */
.stInfo, .stSuccess, .stWarning, .stError {
    background: var(--bg-2) !important;
    border-color: var(--border-m) !important;
    color: var(--text-1) !important;
}
.stCode { background: var(--bg-2) !important; color: var(--teal) !important; }

/* ── MAP NOTE ── */
.map-note {
    background: rgba(245,166,35,.08);
    border: 1px solid rgba(245,166,35,.2);
    border-radius: 12px;
    padding: .7rem 1rem; margin-bottom: 1rem;
    font-size: 13px; color: var(--accent);
}

/* ── EMPTY STATE ── */
.empty {
    text-align: center; padding: 4rem 2rem;
    background: var(--bg-card); border-radius: 20px;
    border: 1px dashed var(--border-m);
}
.empty-icon { font-size: 3rem; margin-bottom: .8rem; }
.empty-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.15rem; font-weight: 700; color: var(--text-1);
}
.empty-sub { font-size: 13px; color: var(--text-3); margin-top: 5px; }

/* ── FOOTER ── */
.footer {
    background: var(--bg-1);
    border-top: 1px solid var(--border);
    text-align: center;
    padding: 1.5rem; font-size: 12px; color: var(--text-3);
}
.footer a { color: var(--accent); text-decoration: none; }
.footer a:hover { color: var(--accent-l); }

/* Caption */
.stCaption { color: var(--text-3) !important; }
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
    ("🍛 Great Food",      lambda t: any(x in t for x in ["good food","tasty","delicious","food is good"])),
    ("🚇 Metro Near",      lambda t: any(x in t for x in ["metro","transport","near bus","walking distance"])),
    ("✨ Very Clean",      lambda t: any(x in t for x in ["clean","neat","maintained","hygienic","tidy"])),
    ("🚀 Fast WiFi",       lambda t: any(x in t for x in ["wifi","internet","fast net","broadband"])),
    ("🔒 Secure",          lambda t: any(x in t for x in ["safe","security","cctv","gated","guard"])),
    ("🌿 Peaceful",        lambda t: any(x in t for x in ["quiet","peaceful","calm","no noise"])),
    ("❄️ AC Rooms",        lambda t: any(x in t for x in ["ac ","air condition","ac room","air-condition"])),
    ("🍽️ Mess Included",  lambda t: any(x in t for x in ["mess","meals included","food included","breakfast"])),
    ("🪳 Hygiene Issue",  lambda t: any(x in t for x in ["cockroach","bugs","dirty","unclean","pest"])),
    ("🥣 Bad Food",        lambda t: any(x in t for x in ["bad food","worst food","repetitive food","tasteless"])),
    ("🚫 No Parking",      lambda t: any(x in t for x in ["no parking","parking issue","congested"])),
    ("📶 Slow WiFi",       lambda t: any(x in t for x in ["slow wifi","no wifi","bad internet","no internet"])),
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

# Dark-mode chart color palette
CHART_COLORS = ["#F5A623","#00C9A7","#5B8CF5","#F0546B","#A78BFA","#34D399","#FB923C","#60A5FA","#F472B6","#FBBF24","#4ADE80"]

def base_layout(height=300):
    return dict(
        height=height, margin=dict(t=5,b=5,l=5,r=5),
        font=dict(family="DM Sans", color="#9AA3B5"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

def style_axes(fig):
    fig.update_xaxes(gridcolor="#1E2335", zerolinecolor="#1E2335", color="#5C6478")
    fig.update_yaxes(gridcolor="#1E2335", zerolinecolor="#1E2335", color="#5C6478")
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
          <div class="hero-divider"></div>
          <div>
            <div class="hero-num-val accent">{total_areas}</div>
            <div class="hero-num-lbl">Areas Covered</div>
          </div>
          <div class="hero-divider"></div>
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


# ── global search bar ──
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
    <div style="padding-top:.4rem;font-size:11px;color:#5C6478;line-height:1.6;">
      Searches name, area,<br>reviews &amp; tags
    </div>""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FILTER LOGIC
# ─────────────────────────────────────────────
fdf = df.copy()
if sel_loc    != "All Areas": fdf = fdf[fdf["Location"] == sel_loc]
if sel_gender != "Any":       fdf = fdf[fdf["Gender"]   == sel_gender]
if sel_share  != "Any":       fdf = fdf[fdf["Sharing"]  == sel_share]
fdf = fdf[fdf["Cost"]   <= budget]
fdf = fdf[fdf["Rating"] >= min_rat]

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

        with right:
            st.markdown("""
            <div class="sec-head">
              <span class="sec-title">Value Matrix</span>
            </div>
            <p style="font-size:13px;color:#5C6478;margin-bottom:.7rem;">
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
            fig.add_hline(y=4.0, line_dash="dot", line_color="#00C9A7",
                          annotation_text="Quality bar (4★)", annotation_font_color="#00C9A7")
            fig.update_layout(
                **base_layout(360),
                legend=dict(orientation="h", y=-0.14, x=0, font_size=10, font_color="#9AA3B5",
                            bgcolor="rgba(0,0,0,0)"),
                xaxis_title="Monthly Rent (₹)", yaxis_title="Rating",
            )
            fig.update_yaxes(range=[0, 5.5])
            fig.update_traces(marker=dict(opacity=0.9, line=dict(width=1.5, color="rgba(255,255,255,.1)")))
            style_axes(fig)
            st.plotly_chart(fig, use_container_width=True)

            area_stats = (fdf.groupby("Location")
                          .agg(avg_rent=("Cost","mean"), avg_rating=("Rating","mean"), count=("Name","count"))
                          .sort_values("avg_rent"))
            rows_html = "".join(f"""
            <div class="irow">
              <span>📍 {area} <span style="color:#3A4155;font-size:11px;">({int(row['count'])} PGs)</span></span>
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
            fig_pie = px.pie(fdf, names="Sharing", hole=0.58,
                             color_discrete_sequence=CHART_COLORS,
                             template="simple_white")
            fig_pie.update_traces(textposition="outside", textinfo="label+percent",
                                  textfont_size=11, textfont_color="#9AA3B5")
            fig_pie.update_layout(**base_layout(300), showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)

        r3, r4 = st.columns(2, gap="large")
        with r3:
            st.markdown('<div class="chart-title">Avg Rent by Area</div><div class="chart-sub">Sorted cheapest → priciest.</div>', unsafe_allow_html=True)
            aa = fdf.groupby("Location")["Cost"].mean().sort_values().reset_index()
            fig_bar = px.bar(aa, x="Cost", y="Location", orientation="h",
                             template="simple_white", color="Cost",
                             color_continuous_scale=["#1A1F2E","#F5A623"],
                             text=aa["Cost"].apply(lambda x: f"₹{int(x):,}"))
            fig_bar.update_layout(**base_layout(280), coloraxis_showscale=False,
                                  showlegend=False, xaxis_title="Avg Rent (₹)", yaxis_title="")
            fig_bar.update_traces(textposition="outside", textfont_color="#9AA3B5")
            style_axes(fig_bar)
            st.plotly_chart(fig_bar, use_container_width=True)

        with r4:
            st.markdown('<div class="chart-title">Ratings Distribution</div><div class="chart-sub">How PGs are rated overall.</div>', unsafe_allow_html=True)
            fig_hist = px.histogram(fdf[fdf["Rating"] > 0], x="Rating", nbins=10,
                                    template="simple_white",
                                    color_discrete_sequence=["#F5A623"])
            fig_hist.update_layout(**base_layout(280), bargap=0.1,
                                   xaxis_title="Rating", yaxis_title="No. of PGs")
            style_axes(fig_hist)
            st.plotly_chart(fig_hist, use_container_width=True)

        r5, r6 = st.columns(2, gap="large")
        with r5:
            st.markdown('<div class="chart-title">Does Paying More Mean Better?</div><div class="chart-sub">Cost vs rating with trend line.</div>', unsafe_allow_html=True)
            fig_sc = px.scatter(fdf[fdf["Rating"] > 0], x="Cost", y="Rating",
                                color="Sharing", hover_name="Name",
                                opacity=0.75,
                                template="simple_white",
                                color_discrete_sequence=CHART_COLORS)
            fig_sc.update_layout(**base_layout(260),
                                 legend=dict(orientation="h", y=-0.2, font_size=11,
                                             font_color="#9AA3B5", bgcolor="rgba(0,0,0,0)"),
                                 xaxis_title="Monthly Rent (₹)", yaxis_title="Rating")
            style_axes(fig_sc)
            st.plotly_chart(fig_sc, use_container_width=True)

        with r6:
            st.markdown('<div class="chart-title">Gender Preference Mix</div><div class="chart-sub">Availability across gender categories.</div>', unsafe_allow_html=True)
            gc = fdf["Gender"].value_counts().reset_index()
            gc.columns = ["Gender","Count"]
            fig_gen = px.bar(gc, x="Gender", y="Count", template="simple_white",
                             color="Gender",
                             color_discrete_sequence=CHART_COLORS)
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
        <div class="map-note">
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
            color_continuous_scale=["#F0546B","#F5A623","#00C9A7"],
            range_color=[0, 5], zoom=11, height=560,
        )
        fig_map.update_layout(
            mapbox_style="carto-darkmatter",
            margin=dict(t=0,b=0,l=0,r=0),
            coloraxis_colorbar=dict(title="Rating", len=0.45, thickness=12,
                                    tickfont=dict(family="DM Sans", size=11, color="#9AA3B5"),
                                    titlefont=dict(color="#9AA3B5")),
            font=dict(family="DM Sans"),
            paper_bgcolor="rgba(0,0,0,0)",
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
  Community data from <strong style="color:#5C6478;">Reddit r/hyderabad</strong>
  &nbsp;·&nbsp; Built with Python & Streamlit
  &nbsp;·&nbsp; <a href="https://github.com/prosuvinhere/Hyd_PG">⭐ Star on GitHub</a>
</div>
""", unsafe_allow_html=True)
