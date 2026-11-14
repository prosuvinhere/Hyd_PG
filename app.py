import math
import os
import re
from datetime import datetime
from urllib.parse import quote_plus

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

# ─────────────────────────────────────────────
#  PAGE CONFIG & STYLING
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Hyd Life | Hyderabad PG Directory & Market Intelligence",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .pg-card {
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 12px;
        padding: 1.15rem 1.35rem;
        margin-bottom: 1rem;
        background-color: rgba(128, 128, 128, 0.04);
    }
    .pg-title {
        font-size: 1.18rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    .pg-subtitle {
        font-size: 0.9rem;
        opacity: 0.85;
        margin-bottom: 0.65rem;
    }
    .tag-pill {
        display: inline-block;
        padding: 0.18rem 0.58rem;
        margin: 0.15rem 0.25rem 0.15rem 0;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 500;
        background-color: rgba(59, 130, 246, 0.14);
        border: 1px solid rgba(59, 130, 246, 0.32);
    }
    .tag-pill-warn {
        display: inline-block;
        padding: 0.18rem 0.58rem;
        margin: 0.15rem 0.25rem 0.15rem 0;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 500;
        background-color: rgba(239, 68, 68, 0.14);
        border: 1px solid rgba(239, 68, 68, 0.35);
    }
    .metric-pill {
        display: inline-block;
        padding: 0.22rem 0.65rem;
        margin-right: 0.4rem;
        margin-bottom: 0.35rem;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 600;
        background-color: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
#  CONSTANTS & GEOSPATIAL REFERENCE DATA
# ─────────────────────────────────────────────
SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1AW4EKm412u_UyYhf1swdhDsP5ikadr3XXeUTMrqvh4w/export?format=csv&gid=1856698473"
)
LOCAL_CSV_PATH = os.path.join(os.path.dirname(__file__), "pg_data.csv")

# Comprehensive coordinates for 30+ Hyderabad localities
COORDS = {
    "Madhapur": (17.4483, 78.3915),
    "Gachibowli": (17.4401, 78.3489),
    "Kondapur": (17.4622, 78.3568),
    "Gowlidoddy": (17.4254, 78.3282),
    "HITEC City": (17.4435, 78.3772),
    "Kokapet": (17.3951, 78.3340),
    "Kukatpally": (17.4948, 78.3996),
    "KPHB": (17.4834, 78.3871),
    "JNTU": (17.4987, 78.3908),
    "SR Nagar": (17.4436, 78.4458),
    "Khajaguda": (17.4178, 78.3652),
    "Nanakramguda": (17.4125, 78.3396),
    "Financial District": (17.4116, 78.3422),
    "Adibatla": (17.2346, 78.5582),
    "Uppal": (17.3984, 78.5583),
    "Madhura Nagar": (17.4368, 78.4369),
    "Dilsukhnagar": (17.3688, 78.5247),
    "Durgam Cheruvu": (17.4426, 78.3875),
    "Shamshabad": (17.2403, 78.4294),
    "Suchitra": (17.5082, 78.4775),
    "Pocharam": (17.4342, 78.6368),
    "Padmarao Nagar": (17.4256, 78.5081),
    "Amberpet": (17.3920, 78.5162),
    "Indira Nagar": (17.4430, 78.3560),
    "Somajiguda": (17.4264, 78.4583),
    "Maisammaguda": (17.5583, 78.4513),
    "TNGO Colony": (17.4241, 78.3368),
    "Begumpet": (17.4447, 78.4664),
    "Narayanguda": (17.3950, 78.4891),
    "Jubilee Hills": (17.4325, 78.4070),
    "Banjara Hills": (17.4123, 78.4389),
    "Manikonda": (17.4018, 78.3846),
    "Hafeezpet": (17.4856, 78.3526),
    "Ameerpet": (17.4375, 78.4483),
    "Unknown": (17.4400, 78.3800),
}

# Major Hyderabad IT / Office Hubs for commute calculations
IT_HUBS = {
    "Mindspace / HITEC City": (17.4422, 78.3774),
    "DLF Cyber City (Gachibowli)": (17.4485, 78.3548),
    "Financial District / WaveRock": (17.4158, 78.3426),
    "Knowledge City / Raidurg": (17.4344, 78.3827),
    "Kondapur / Botanical Garden": (17.4567, 78.3522),
    "Kokapet SEZ / Neopolis": (17.3926, 78.3321),
    "Ameerpet / Begumpet Corridor": (17.4399, 78.4563),
    "Pocharam / Infosys SEZ": (17.4418, 78.6472),
    "Adibatla / TCS SEZ": (17.2321, 78.5624),
}

# Key Hyderabad Metro Stations along Red, Blue, and Green Lines
METRO_STATIONS = [
    # Blue Line (Raidurg <-> Nagole)
    {"station": "Raidurg", "line": "Blue Line", "lat": 17.4422, "lon": 78.3774},
    {"station": "HITEC City", "line": "Blue Line", "lat": 17.4489, "lon": 78.3832},
    {"station": "Durgam Cheruvu", "line": "Blue Line", "lat": 17.4428, "lon": 78.3875},
    {"station": "Madhapur", "line": "Blue Line", "lat": 17.4372, "lon": 78.3983},
    {"station": "Peddamma Gudi", "line": "Blue Line", "lat": 17.4306, "lon": 78.4083},
    {"station": "Jubilee Hills Check Post", "line": "Blue Line", "lat": 17.4265, "lon": 78.4198},
    {"station": "Ameerpet (Interchange)", "line": "Blue Line", "lat": 17.4357, "lon": 78.4446},
    {"station": "Begumpet", "line": "Blue Line", "lat": 17.4439, "lon": 78.4607},
    {"station": "Secunderabad East", "line": "Blue Line", "lat": 17.4354, "lon": 78.5046},
    {"station": "Uppal", "line": "Blue Line", "lat": 17.4002, "lon": 78.5601},
    {"station": "Nagole", "line": "Blue Line", "lat": 17.3908, "lon": 78.5594},
    # Red Line (Miyapur <-> LB Nagar)
    {"station": "Miyapur", "line": "Red Line", "lat": 17.4967, "lon": 78.3731},
    {"station": "JNTU College", "line": "Red Line", "lat": 17.4986, "lon": 78.3888},
    {"station": "KPHB Colony", "line": "Red Line", "lat": 17.4938, "lon": 78.4017},
    {"station": "Kukatpally", "line": "Red Line", "lat": 17.4851, "lon": 78.4095},
    {"station": "SR Nagar", "line": "Red Line", "lat": 17.4440, "lon": 78.4414},
    {"station": "Punjagutta", "line": "Red Line", "lat": 17.4286, "lon": 78.4510},
    {"station": "MGBS (Interchange)", "line": "Red Line", "lat": 17.3788, "lon": 78.4800},
    {"station": "Dilsukhnagar", "line": "Red Line", "lat": 17.3685, "lon": 78.5257},
    {"station": "Chaitanyapuri", "line": "Red Line", "lat": 17.3682, "lon": 78.5361},
    {"station": "LB Nagar", "line": "Red Line", "lat": 17.3457, "lon": 78.5522},
    # Green Line (JBS Parade Ground <-> MGBS)
    {"station": "JBS Parade Ground", "line": "Green Line", "lat": 17.4437, "lon": 78.4973},
    {"station": "RTC X Roads", "line": "Green Line", "lat": 17.4072, "lon": 78.4966},
    {"station": "Narayanguda", "line": "Green Line", "lat": 17.3944, "lon": 78.4900},
]


# ─────────────────────────────────────────────
#  HELPER & CLEANING FUNCTIONS
# ─────────────────────────────────────────────
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in kilometers between two lat/lon points."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def clean_cost(val) -> float:
    """
    Standardizes messy monthly rent inputs:
    - Currency symbols & commas ('₹12,000' -> 12000)
    - Ranges ('5000-6000' or '5k-6k' -> 5500)
    - Shorthand in thousands ('8.5' -> 8500, '12.5' -> 12500, '22' -> 22000)
    - Extra zero typos ('120000' -> 12000)
    """
    if pd.isna(val):
        return 0.0
    s = str(val).lower().replace("₹", "").replace("rs", "").replace(",", "").strip()
    if not s:
        return 0.0

    def _parse_single(token: str) -> float:
        token = token.strip()
        is_k = "k" in token
        token = re.sub(r"[^0-9.]", "", token)
        if not token:
            return 0.0
        try:
            num = float(token)
        except ValueError:
            return 0.0
        if is_k or (0 < num <= 65):
            num *= 1000.0
        elif num >= 65000:
            # Fix accidental extra trailing zero (e.g., 120000 -> 12000)
            while num >= 65000:
                num /= 10.0
        return num

    if "-" in s:
        parts = [p for p in s.split("-") if p.strip()]
        if len(parts) >= 2:
            v1, v2 = _parse_single(parts[0]), _parse_single(parts[1])
            if v1 > 0 and v2 > 0:
                return (v1 + v2) / 2.0
    return _parse_single(s)


def normalize_location(raw_loc) -> tuple[str, str]:
    """
    Returns (CanonicalLocation, ExtractedMapURL).
    Unifies spelling variants and extracts embedded Google Maps links.
    """
    if pd.isna(raw_loc):
        return "Unknown", ""
    s = str(raw_loc).strip()
    url_match = re.search(r"(https?://\S+)", s)
    extracted_url = url_match.group(1) if url_match else ""

    low = s.lower()
    if "maps.app.goo.gl" in low or "delight inn" in low:
        return "Kondapur", extracted_url
    if "pocharam" in low or "singapore township" in low:
        return "Pocharam", extracted_url
    if "nanakramguda" in low:
        return "Nanakramguda", extracted_url
    if "dilshuk" in low or "dilsukh" in low:
        return "Dilsukhnagar", extracted_url
    if "somju" in low or "somaji" in low:
        return "Somajiguda", extracted_url
    if "gacchi" in low or "gachibowli" in low:
        return "Gachibowli", extracted_url
    if "hitec" in low or "hi-tech" in low or "hitech" in low:
        return "HITEC City", extracted_url
    if "kphb" in low:
        return "KPHB", extracted_url
    if "jntu" in low:
        return "JNTU", extracted_url
    if "sr nagar" in low or "s r nagar" in low:
        return "SR Nagar", extracted_url
    if "tngo" in low:
        return "TNGO Colony", extracted_url
    if "financial" in low:
        return "Financial District", extracted_url

    cleaned = s.title()
    return (cleaned if cleaned in COORDS else cleaned), extracted_url


def normalize_pg_type(raw_type) -> str:
    """Standardizes Type of PG into Male Only, Female Only, or Co-Living."""
    if pd.isna(raw_type):
        return "Co-Living"
    low = str(raw_type).lower()
    if "co living" in low or "coliving" in low or "both" in low:
        return "Co-Living"
    if "female" in low or "women" in low or "ladies" in low or "girl" in low:
        return "Female Only"
    if "male" in low or "men" in low or "boy" in low or "gents" in low:
        return "Male Only"
    return "Co-Living"


def normalize_parking(raw_parking) -> str:
    """Categorizes messy parking descriptions into clean filterable buckets."""
    if pd.isna(raw_parking) or not str(raw_parking).strip():
        return "Unknown"
    low = str(raw_parking).lower()
    if "no parking" in low and "infront" not in low and "front" not in low:
        return "No Parking"
    if "4-wheeler" in low or "4 wheeler" in low or "four wheeler" in low or "both" in low or "spacious" in low:
        return "2 & 4 Wheeler"
    if "congested" in low or "less space" in low:
        return "2-Wheeler (Congested)"
    if "front" in low or "empty site" in low or "outside" in low:
        return "Street / Outside"
    if "2-wheeler" in low or "2 wheeler" in low:
        return "2-Wheeler"
    return "2-Wheeler"


def clean_phone(raw_phone) -> tuple[str, str]:
    """
    Cleans phone numbers (removes float '.0', '+91', leading '0') and returns:
    (FormattedDisplayPhone, Raw10DigitForLinks).
    """
    if pd.isna(raw_phone):
        return "Not Provided", ""
    s = str(raw_phone).strip()
    if s.endswith(".0"):
        s = s[:-2]
    digits = re.sub(r"\D", "", s)
    if not digits or set(digits) == {"0"}:
        return "Not Provided", ""
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    elif len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    if len(digits) == 10:
        return f"+91 {digits[:5]} {digits[5:]}", digits
    return s, digits


def extract_smart_tags(row: pd.Series) -> list[str]:
    """
    Smart Tagging Engine: scans review text and structured fields for positive
    amenities and red-flag warnings.
    """
    text = str(row.get("Comments", "")).lower()
    tags = []

    # Wi-Fi signals
    if any(w in text for w in ["slow wifi", "slow wi-fi", "wifi is slow", "wi-fi speed can be slow", "wifi speed low", "ping is shit"]):
        tags.append("🐢 Slow Wi-Fi")
    elif any(w in text for w in ["wifi", "wi-fi", "internet"]):
        tags.append("🚀 Good Wi-Fi")

    # Transit & Metro
    if any(w in text for w in ["metro", "bus stop", "public transport", "walkable", "walking distance"]):
        tags.append("🚇 Near Transit/Metro")

    # Gym & Recreation
    if "no gym" not in text and any(w in text for w in ["gym", "fitness"]):
        tags.append("🏋️ Gym")
    if "no game" not in text and any(w in text for w in ["pool table", "indoor games", "gaming zone", "box cricket", "play area"]):
        tags.append("🎮 Games/Recreation")

    # Room & Appliances
    if any(w in text for w in [" ac ", " ac,", "ac room", "air condition", "fully furnished with ac", "ac 2", "ac 3"]):
        tags.append("❄️ AC")
    if any(w in text for w in ["washing machine", "laundry"]):
        tags.append("🧺 Laundry/Washing")
    if any(w in text for w in ["power backup", "inverter", "generator"]):
        tags.append("🔋 Power Backup")
    if any(w in text for w in ["fridge", "self kitchen", "self cooking", "cook your own", "induction"]):
        tags.append("🍳 Fridge/Self-Cook")
    if any(w in text for w in ["cctv", "fingerprint", "biometric", "security guard", "security uncle", "access card"]):
        tags.append("🔒 CCTV/Security")

    # Structured attributes
    if row.get("Electricity") == "Included in rent":
        tags.append("⚡ Elec. Included")
    if row.get("ParkingCategory") == "2 & 4 Wheeler":
        tags.append("🚗 4W Parking")

    # Red flags / Warnings
    if any(w in text for w in ["bed bug", "bedbug", "cockroach", "insects", "pest", "rot"]):
        tags.append("⚠️ Pest Alert")
    if any(w in text for w in ["rude", "horrible", "not give back the advance", "deposit", "micromanager", "trash"]):
        tags.append("⚠️ Mgmt/Deposit Alert")

    return tags


# ─────────────────────────────────────────────
#  DATA LOADING & CACHING
# ─────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner="Loading & analyzing Hyderabad PG directory...")
def load_data() -> tuple[pd.DataFrame, str]:
    """
    Loads PG data from the live Google Sheet with automatic fallback to local pg_data.csv.
    Returns (cleaned_dataframe, data_source_label).
    """
    source_label = "Live Google Sheet"
    try:
        resp = requests.get(SHEET_CSV_URL, timeout=6)
        resp.raise_for_status()
        from io import StringIO
        raw_df = pd.read_csv(StringIO(resp.text), dtype={"PG Owner Phone number": str})
    except Exception:
        source_label = "Local Snapshot (pg_data.csv)"
        if os.path.exists(LOCAL_CSV_PATH):
            raw_df = pd.read_csv(LOCAL_CSV_PATH, dtype={"PG Owner Phone number": str})
        else:
            return pd.DataFrame(), "Unavailable"

    df = raw_df.copy()
    df.columns = df.columns.str.strip()
    df.rename(
        columns={
            "Name of PG/Hostel:": "Name",
            "Type of PG": "PGTypeRaw",
            "🌍 Location:": "LocationRaw",
            "🏡Type of Sharing:": "Sharing",
            "💰 Monthly Cost (₹):": "Cost",
            "🍴 Food Quality:": "FoodRating",
            "🚲Parking Space": "ParkingRaw",
            "🏢 Room Space:": "RoomSpace",
            "⚡Electricity Bill:": "Electricity",
            "Overall Rating:": "Rating",
            "Additional Comments:": "Comments",
            "Contributor Reddit Username": "Contributor",
            "PG Owner Phone number": "PhoneRaw",
            "Contributor Gender": "ContributorGender",
        },
        inplace=True,
    )

    # Clean core fields
    df["Name"] = df["Name"].fillna("Unnamed PG").astype(str).str.strip()
    df["Cost"] = df["Cost"].apply(clean_cost)
    df = df[(df["Cost"] >= 2000) & (df["Cost"] <= 65000)].copy()

    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce").fillna(0.0).clip(0.0, 5.0)
    df["FoodRating"] = pd.to_numeric(df["FoodRating"], errors="coerce").fillna(0.0).clip(0.0, 5.0)

    # Location & Map URLs
    loc_parsed = df["LocationRaw"].apply(normalize_location)
    df["Location"] = [item[0] for item in loc_parsed]
    df["ExtraMapURL"] = [item[1] for item in loc_parsed]

    # PG Type (Male Only / Female Only / Co-Living)
    df["PGType"] = df["PGTypeRaw"].apply(normalize_pg_type)

    # Sharing, Room Space, Electricity, Parking
    df["Sharing"] = df["Sharing"].fillna("Unknown").astype(str).str.strip()
    df["RoomSpace"] = df["RoomSpace"].fillna("Average").astype(str).str.strip()
    df["Electricity"] = df["Electricity"].fillna("Included in rent").astype(str).str.strip()
    df["ParkingRaw"] = df["ParkingRaw"].fillna("Not specified").astype(str).str.strip()
    df["ParkingCategory"] = df["ParkingRaw"].apply(normalize_parking)

    # Comments, Contributor, Timestamp
    df["Comments"] = df["Comments"].fillna("").astype(str).str.strip()
    df["Contributor"] = df["Contributor"].fillna("Anonymous").astype(str).str.strip()
    df["Contributor"] = df["Contributor"].replace({"": "Anonymous"})
    df["SubmittedAt"] = pd.to_datetime(df.get("Timestamp"), errors="coerce")

    # Phone numbers & links
    phone_parsed = df["PhoneRaw"].apply(clean_phone)
    df["Phone"] = [item[0] for item in phone_parsed]
    df["PhoneDigits"] = [item[1] for item in phone_parsed]

    # Smart Tags
    df["TagList"] = df.apply(extract_smart_tags, axis=1)
    df["SmartTags"] = df["TagList"].apply(lambda tags: "  ".join(tags) if tags else "—")

    # Value Score = ((Rating^2) / Cost) * 5000 (as documented in README)
    df["ValueScore"] = np.where(
        df["Cost"] > 0,
        ((df["Rating"] ** 2) / df["Cost"]) * 5000.0,
        0.0,
    ).round(2)

    # Deterministic Coordinates + Gaussian Jitter for visual separation
    rng = np.random.default_rng(42)
    base_coords = df["Location"].map(lambda loc: COORDS.get(loc, COORDS["Unknown"]))
    df["lat"] = [c[0] for c in base_coords] + rng.normal(0, 0.0028, len(df))
    df["lon"] = [c[1] for c in base_coords] + rng.normal(0, 0.0028, len(df))

    # Nearest Metro Station & Distance
    nearest_names, nearest_lines, nearest_dists = [], [], []
    for _, row in df.iterrows():
        best_st = min(
            METRO_STATIONS,
            key=lambda st_item: haversine_km(row["lat"], row["lon"], st_item["lat"], st_item["lon"]),
        )
        dist = haversine_km(row["lat"], row["lon"], best_st["lat"], best_st["lon"])
        nearest_names.append(best_st["station"])
        nearest_lines.append(best_st["line"])
        nearest_dists.append(round(dist, 1))

    df["NearestMetro"] = nearest_names
    df["MetroLine"] = nearest_lines
    df["MetroDistKm"] = nearest_dists

    # Google Maps search link
    df["MapsURL"] = df.apply(
        lambda r: r["ExtraMapURL"]
        if r["ExtraMapURL"]
        else f"https://www.google.com/maps/search/?api=1&query={quote_plus(str(r['Name']) + ' ' + str(r['Location']) + ' Hyderabad')}",
        axis=1,
    )

    return df.reset_index(drop=True), source_label


# ─────────────────────────────────────────────
#  MONTHLY USERS COUNTER (NON-BLOCKING)
# ─────────────────────────────────────────────
def get_monthly_users() -> int:
    namespace = "hyderabad_pg_directory_reddit"
    current_month = datetime.now().strftime("%Y_%m")
    counter_name = f"monthly_users_{current_month}"
    api_url = f"https://api.counterapi.dev/v1/{namespace}/{counter_name}"

    if "view_logged" not in st.session_state:
        st.session_state.view_logged = True
        try:
            response = requests.get(f"{api_url}/up", timeout=2.5)
            if response.status_code == 200:
                st.session_state.current_monthly_users = response.json().get("count", 0)
        except Exception:
            st.session_state.current_monthly_users = st.session_state.get("current_monthly_users", 0)
    return st.session_state.get("current_monthly_users", 0)


# ─────────────────────────────────────────────
#  SIDEBAR NAVIGATION & STATUS
# ─────────────────────────────────────────────
df_all, data_source = load_data()
monthly_users = get_monthly_users()

with st.sidebar:
    st.markdown("## 🏠 Hyd Life")
    st.caption("Crowdsourced Hyderabad PG Directory & Market Intelligence")

    page = st.radio(
        "Navigation",
        [
            "🔍 Search, Compare & Analytics",
            "🚇 Metro & Commute Map",
            "➕ Add a PG & Community Info",
        ],
    )

    st.divider()
    st.markdown("**📡 Data Pipeline**")
    st.caption(f"Source: `{data_source}`")
    if not df_all.empty:
        st.caption(
            f"**{len(df_all)}** verified reviews across **{df_all['Location'].nunique()}** localities"
        )
    if st.button("🔄 Refresh Live Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    st.metric("📅 Monthly Active Users", f"{monthly_users:,}" if monthly_users > 0 else "Live")
    st.caption("100% community-driven by **r/hyderabad** • Zero brokers")


# ══════════════════════════════════════════════
#  PAGE 1: SEARCH, COMPARE & MARKET ANALYTICS
# ══════════════════════════════════════════════
if page == "🔍 Search, Compare & Analytics":
    st.title("🏠 Hyderabad PG Finder & Market Intelligence")
    st.markdown(
        "Explore crowd-verified PGs & Co-Living spaces across Hyderabad with **Smart Review Tags**, "
        "**Value-for-Money scoring**, **side-by-side comparison**, and **real-time market analytics**."
    )

    if df_all.empty:
        st.error("Unable to load PG dataset. Please check your connection or `pg_data.csv`.")
        st.stop()

    # ── PRIMARY FILTERS ──
    fcol1, fcol2, fcol3, fcol4, fcol5 = st.columns([1.4, 1.0, 1.0, 1.3, 1.0])
    with fcol1:
        all_locs = sorted(df_all["Location"].unique().tolist())
        sel_loc = st.multiselect("📍 Locality / Area", all_locs, default=[], placeholder="All Areas")
    with fcol2:
        pg_types = ["Any", "Male Only", "Female Only", "Co-Living"]
        sel_pg_type = st.selectbox("👥 PG Type", pg_types)
    with fcol3:
        sharing_order = ["Any", "Single", "Two Sharing", "Triple Sharing", "Four Sharing", "Five Sharing"]
        avail_sharing = ["Any"] + [s for s in sharing_order[1:] if s in df_all["Sharing"].unique()]
        sel_share = st.selectbox("🛏️ Room Sharing", avail_sharing)
    with fcol4:
        min_cost_val = int(df_all["Cost"].min() // 500 * 500)
        max_cost_val = int(math.ceil(df_all["Cost"].max() / 500.0) * 500)
        budget_range = st.slider(
            "💰 Monthly Budget Range (₹)",
            min_value=min_cost_val,
            max_value=max_cost_val,
            value=(min_cost_val, min(25000, max_cost_val)),
            step=500,
        )
    with fcol5:
        min_rat = st.slider("⭐ Min Overall Rating", 0.0, 5.0, 0.0, 0.5)

    # ── SEARCH & ADVANCED FILTERS ──
    scol1, scol2 = st.columns([2.2, 1.0])
    with scol1:
        search_query = st.text_input(
            "🔎 Search by PG name, area, landmark, or review keywords (e.g., 'gym', 'metro', 'ac', 'deloitte', 'wifi')...",
            placeholder="Type keywords to filter listings...",
        )
    with scol2:
        sort_by = st.selectbox(
            "🔃 Sort Listings By",
            [
                "Best Value Score (High → Low)",
                "Overall Rating (High → Low)",
                "Monthly Rent (Low → High)",
                "Monthly Rent (High → Low)",
                "Food Quality (High → Low)",
                "Most Recent Submissions",
            ],
        )

    with st.expander("⚙️ Advanced Filters (Food Quality, Electricity, Room Space, Parking & Smart Tags)"):
        acol1, acol2, acol3, acol4, acol5 = st.columns(5)
        with acol1:
            min_food = st.slider("🍴 Min Food Rating", 0.0, 5.0, 0.0, 0.5)
        with acol2:
            sel_elec = st.selectbox(
                "⚡ Electricity Bill",
                ["Any", "Included in rent", "Separate bill"],
            )
        with acol3:
            sel_space = st.multiselect(
                "🏢 Room Space",
                ["Spacious", "Average", "Cramped"],
                default=[],
                placeholder="Any Space",
            )
        with acol4:
            all_parking = sorted(df_all["ParkingCategory"].unique().tolist())
            sel_parking = st.multiselect(
                "🚲 Parking Availability",
                all_parking,
                default=[],
                placeholder="Any Parking",
            )
        with acol5:
            positive_tags = [
                "🚀 Good Wi-Fi",
                "🚇 Near Transit/Metro",
                "🏋️ Gym",
                "❄️ AC",
                "🧺 Laundry/Washing",
                "🔋 Power Backup",
                "🍳 Fridge/Self-Cook",
                "🔒 CCTV/Security",
            ]
            sel_tags = st.multiselect(
                "🏷️ Must-Have Smart Tags",
                positive_tags,
                default=[],
                placeholder="Select amenities...",
            )
        hide_red_flags = st.checkbox(
            "🛡️ Hide listings with Pest or Management/Deposit warning tags",
            value=False,
        )

    # ── APPLY FILTERS ──
    fdf = df_all.copy()
    if sel_loc:
        fdf = fdf[fdf["Location"].isin(sel_loc)]
    if sel_pg_type != "Any":
        fdf = fdf[fdf["PGType"] == sel_pg_type]
    if sel_share != "Any":
        fdf = fdf[fdf["Sharing"] == sel_share]
    fdf = fdf[(fdf["Cost"] >= budget_range[0]) & (fdf["Cost"] <= budget_range[1])]
    fdf = fdf[(fdf["Rating"] >= min_rat) & (fdf["FoodRating"] >= min_food)]

    if sel_elec != "Any":
        fdf = fdf[fdf["Electricity"] == sel_elec]
    if sel_space:
        fdf = fdf[fdf["RoomSpace"].isin(sel_space)]
    if sel_parking:
        fdf = fdf[fdf["ParkingCategory"].isin(sel_parking)]
    if sel_tags:
        fdf = fdf[fdf["TagList"].apply(lambda tlist: all(tag in tlist for tag in sel_tags))]
    if hide_red_flags:
        fdf = fdf[
            ~fdf["TagList"].apply(
                lambda tlist: ("⚠️ Pest Alert" in tlist) or ("⚠️ Mgmt/Deposit Alert" in tlist)
            )
        ]

    if search_query.strip():
        q = search_query.strip()
        mask = (
            fdf["Name"].str.contains(q, case=False, na=False)
            | fdf["Location"].str.contains(q, case=False, na=False)
            | fdf["Comments"].str.contains(q, case=False, na=False)
            | fdf["SmartTags"].str.contains(q, case=False, na=False)
        )
        fdf = fdf[mask]

    # Sort logic
    if sort_by == "Best Value Score (High → Low)":
        fdf = fdf.sort_values(["ValueScore", "Rating", "Cost"], ascending=[False, False, True])
    elif sort_by == "Overall Rating (High → Low)":
        fdf = fdf.sort_values(["Rating", "FoodRating", "Cost"], ascending=[False, False, True])
    elif sort_by == "Monthly Rent (Low → High)":
        fdf = fdf.sort_values(["Cost", "Rating"], ascending=[True, False])
    elif sort_by == "Monthly Rent (High → Low)":
        fdf = fdf.sort_values(["Cost", "Rating"], ascending=[False, False])
    elif sort_by == "Food Quality (High → Low)":
        fdf = fdf.sort_values(["FoodRating", "Rating", "Cost"], ascending=[False, False, True])
    elif sort_by == "Most Recent Submissions":
        fdf = fdf.sort_values("SubmittedAt", ascending=False, na_position="last")

    fdf = fdf.reset_index(drop=True)

    st.divider()

    if fdf.empty:
        st.warning("No PGs match your current filter criteria. Try widening your budget range or clearing a filter.")
        st.stop()

    # ── KPI SUMMARY ROW ──
    k1, k2, k3, k4, k5 = st.columns(5)
    rated_pgs = fdf[fdf["Rating"] > 0]
    avg_rent = fdf["Cost"].mean()
    med_rent = fdf["Cost"].median()
    avg_rating = rated_pgs["Rating"].mean() if not rated_pgs.empty else 0.0
    avg_food = fdf[fdf["FoodRating"] > 0]["FoodRating"].mean() if not fdf[fdf["FoodRating"] > 0].empty else 0.0
    try:
        cheap_area = fdf.groupby("Location")["Cost"].median().idxmin()
    except Exception:
        cheap_area = "—"
    top_val_pg = fdf.sort_values("ValueScore", ascending=False).iloc[0]["Name"]

    k1.metric("Matching PGs", f"{len(fdf)}", f"{len(fdf) - len(df_all)} filtered" if len(fdf) != len(df_all) else "All listings")
    k2.metric("Average / Median Rent", f"₹{int(avg_rent):,}", f"Median: ₹{int(med_rent):,}", delta_color="off")
    k3.metric("Avg Overall Rating", f"{avg_rating:.2f} ⭐", f"Food Avg: {avg_food:.1f} 🍴", delta_color="off")
    k4.metric("Most Affordable Hub", cheap_area)
    k5.metric("Top Value Pick", top_val_pg[:22] + ("…" if len(top_val_pg) > 22 else ""))

    st.write("")

    # ── MAIN CONTENT TABS ──
    tab_dir, tab_cards, tab_compare, tab_analytics = st.tabs(
        [
            f"📋 PG Directory Table ({len(fdf)})",
            "🗂️ Detailed Review Cards",
            "⚖️ Compare PGs Side-by-Side",
            "📊 Market Analytics & Insights",
        ]
    )

    # ── TAB 1: INTERACTIVE DIRECTORY TABLE ──
    with tab_dir:
        tcol1, tcol2 = st.columns([3, 1])
        with tcol1:
            st.caption(
                "💡 **Tip:** Click any column header to sort, hover over truncated reviews to read the full text, "
                "or click the **Maps** link to locate the PG on Google Maps."
            )
        with tcol2:
            csv_bytes = fdf[
                [
                    "Name",
                    "Location",
                    "PGType",
                    "Sharing",
                    "Cost",
                    "Rating",
                    "FoodRating",
                    "ValueScore",
                    "RoomSpace",
                    "Electricity",
                    "ParkingCategory",
                    "SmartTags",
                    "Phone",
                    "NearestMetro",
                    "MetroDistKm",
                    "Comments",
                ]
            ].to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Export Filtered CSV",
                data=csv_bytes,
                file_name="hyderabad_pgs_filtered.csv",
                mime="text/csv",
                use_container_width=True,
            )

        display_cols = [
            "Name",
            "Location",
            "PGType",
            "Sharing",
            "Cost",
            "Rating",
            "FoodRating",
            "ValueScore",
            "SmartTags",
            "RoomSpace",
            "Electricity",
            "ParkingCategory",
            "Phone",
            "MapsURL",
            "Comments",
        ]

        st.dataframe(
            fdf[display_cols],
            hide_index=True,
            use_container_width=True,
            height=520,
            column_config={
                "Name": st.column_config.TextColumn("PG / Hostel Name", width="medium"),
                "Location": st.column_config.TextColumn("Area", width="small"),
                "PGType": st.column_config.TextColumn("PG Type", width="small"),
                "Sharing": st.column_config.TextColumn("Sharing", width="small"),
                "Cost": st.column_config.NumberColumn("Rent / Mo", format="₹%d"),
                "Rating": st.column_config.NumberColumn("Rating", format="%.1f ⭐"),
                "FoodRating": st.column_config.NumberColumn("Food", format="%.1f 🍴"),
                "ValueScore": st.column_config.ProgressColumn(
                    "Value Score",
                    help="Value Score = (Rating² / Monthly Cost) × 5000",
                    format="%.1f",
                    min_value=0,
                    max_value=float(max(15.0, df_all["ValueScore"].max())),
                ),
                "SmartTags": st.column_config.TextColumn("Smart Tags", width="medium"),
                "RoomSpace": st.column_config.TextColumn("Room Space", width="small"),
                "Electricity": st.column_config.TextColumn("Electricity", width="small"),
                "ParkingCategory": st.column_config.TextColumn("Parking", width="small"),
                "Phone": st.column_config.TextColumn("Owner Phone", width="small"),
                "MapsURL": st.column_config.LinkColumn("Map", display_text="📍 Open Map", width="small"),
                "Comments": st.column_config.TextColumn("Community Review", width="large"),
            },
        )

    # ── TAB 2: DETAILED REVIEW CARDS ──
    with tab_cards:
        st.caption("Browse rich community review cards with extracted amenity tags, metro proximity, and direct owner contacts.")
        page_size = 12
        total_pages = max(1, math.ceil(len(fdf) / page_size))
        pcol1, pcol2 = st.columns([1, 3])
        with pcol1:
            curr_page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
        with pcol2:
            st.write("")
            st.caption(f"Showing listings {(curr_page - 1) * page_size + 1}–{min(curr_page * page_size, len(fdf))} of {len(fdf)}")

        subset = fdf.iloc[(curr_page - 1) * page_size : curr_page * page_size]
        for idx, row in subset.iterrows():
            tags_html = "".join(
                f'<span class="{"tag-pill-warn" if "⚠️" in t else "tag-pill"}">{t}</span>'
                for t in row["TagList"]
            )
            if not tags_html:
                tags_html = '<span class="tag-pill">📝 Standard Listing</span>'

            comment_body = (
                row["Comments"].replace("\n", "<br>")
                if row["Comments"]
                else "<i>No written review comment provided by the contributor.</i>"
            )
            date_str = (
                row["SubmittedAt"].strftime("%b %d, %Y")
                if pd.notna(row["SubmittedAt"])
                else "Community Submission"
            )
            phone_action = (
                f"📞 **{row['Phone']}** · [💬 WhatsApp Owner](https://wa.me/91{row['PhoneDigits']})"
                if row["PhoneDigits"]
                else "📞 *Phone not provided*"
            )

            st.markdown(
                f"""
                <div class="pg-card">
                    <div class="pg-title">{row['Name']} — <span style="color:#10b981;">₹{int(row['Cost']):,}/mo</span></div>
                    <div class="pg-subtitle">
                        📍 <b>{row['Location']}</b> &nbsp;|&nbsp; 👥 <b>{row['PGType']}</b> &nbsp;|&nbsp; 🛏️ <b>{row['Sharing']}</b>
                        &nbsp;|&nbsp; 🚇 ~{row['MetroDistKm']} km to <b>{row['NearestMetro']}</b> ({row['MetroLine']})
                    </div>
                    <div style="margin-bottom:0.6rem;">
                        <span class="metric-pill">⭐ Overall: {row['Rating']:.1f}/5</span>
                        <span class="metric-pill">🍴 Food: {row['FoodRating']:.1f}/5</span>
                        <span class="metric-pill">💎 Value Score: {row['ValueScore']:.1f}</span>
                        <span class="metric-pill">🏢 Space: {row['RoomSpace']}</span>
                        <span class="metric-pill">⚡ {row['Electricity']}</span>
                        <span class="metric-pill">🚲 Parking: {row['ParkingCategory']}</span>
                    </div>
                    <div style="margin-bottom:0.65rem;">{tags_html}</div>
                    <div style="font-size:0.93rem; line-height:1.5; margin-bottom:0.6rem;">{comment_body}</div>
                    <div style="font-size:0.8rem; opacity:0.75;">
                        👤 Reviewed by <b>{row['Contributor']}</b> on {date_str}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            bcol1, bcol2, _ = st.columns([1.2, 2.2, 3])
            with bcol1:
                st.link_button("📍 View on Google Maps", row["MapsURL"], use_container_width=True)
            with bcol2:
                st.markdown(phone_action)

    # ── TAB 3: SIDE-BY-SIDE COMPARISON ──
    with tab_compare:
        st.subheader("⚖️ Compare PGs Side-by-Side")
        st.caption("Select 2 to 4 PGs from your filtered results to compare rent, ratings, food quality, and amenities head-to-head.")

        fdf["CompareLabel"] = fdf.apply(
            lambda r: f"{r['Name']} ({r['Location']} • {r['Sharing']} • ₹{int(r['Cost']):,})",
            axis=1,
        )
        default_labels = fdf["CompareLabel"].head(min(3, len(fdf))).tolist()
        selected_labels = st.multiselect(
            "Select PGs to Compare (up to 4)",
            options=fdf["CompareLabel"].tolist(),
            default=default_labels,
            max_selections=4,
        )

        if len(selected_labels) < 2:
            st.info("Please select at least 2 PGs above to view the side-by-side comparison.")
        else:
            comp_df = fdf[fdf["CompareLabel"].isin(selected_labels)].copy()
            cols = st.columns(len(comp_df))
            for col_ui, (_, crow) in zip(cols, comp_df.iterrows()):
                with col_ui:
                    st.markdown(f"#### {crow['Name']}")
                    st.caption(f"📍 {crow['Location']} • {crow['PGType']}")
                    st.metric("Monthly Rent", f"₹{int(crow['Cost']):,}")
                    st.metric("Value Score", f"{crow['ValueScore']:.2f}")
                    st.markdown(
                        f"""
                        - **Sharing:** {crow['Sharing']}
                        - **Overall Rating:** {crow['Rating']:.1f} / 5 ⭐
                        - **Food Quality:** {crow['FoodRating']:.1f} / 5 🍴
                        - **Room Space:** {crow['RoomSpace']}
                        - **Electricity:** {crow['Electricity']}
                        - **Parking:** {crow['ParkingCategory']}
                        - **Nearest Metro:** {crow['NearestMetro']} (~{crow['MetroDistKm']} km)
                        - **Phone:** {crow['Phone']}
                        - **Smart Tags:** {crow['SmartTags']}
                        """
                    )
                    with st.expander("Read Full Review"):
                        st.write(crow["Comments"] if crow["Comments"] else "No comment provided.")
                    st.link_button("📍 Open in Google Maps", crow["MapsURL"], use_container_width=True)

            st.divider()
            st.markdown("#### 📊 Multi-Metric Comparison Chart")
            chart_df = comp_df[["Name", "Rating", "FoodRating", "ValueScore"]].melt(
                id_vars="Name",
                var_name="Metric",
                value_name="Score",
            )
            fig_comp = px.bar(
                chart_df,
                x="Name",
                y="Score",
                color="Metric",
                barmode="group",
                text_auto=".1f",
                color_discrete_sequence=["#3b82f6", "#10b981", "#f59e0b"],
            )
            fig_comp.update_layout(height=360, xaxis_title="", yaxis_title="Score")
            st.plotly_chart(fig_comp, use_container_width=True)

    # ── TAB 4: MARKET ANALYTICS & INSIGHTS ──
    with tab_analytics:
        st.caption(f"Real-time structural and pricing analytics across **{len(fdf)}** matching PG accommodations.")

        r1c1, r1c2 = st.columns(2)
        with r1c1:
            st.subheader("💰 Monthly Rent Distribution by PG Type")
            fig_hist = px.histogram(
                fdf,
                x="Cost",
                color="PGType",
                nbins=18,
                marginal="box",
                color_discrete_map={
                    "Co-Living": "#6366f1",
                    "Male Only": "#3b82f6",
                    "Female Only": "#ec4899",
                },
                labels={"Cost": "Monthly Rent (₹)", "PGType": "PG Type"},
            )
            fig_hist.update_layout(height=380, bargap=0.08)
            st.plotly_chart(fig_hist, use_container_width=True)

        with r1c2:
            st.subheader("🛏️ Room Sharing & Electricity Breakdown")
            fig_sun = px.sunburst(
                fdf,
                path=["PGType", "Sharing", "Electricity"],
                color="PGType",
                color_discrete_map={
                    "Co-Living": "#6366f1",
                    "Male Only": "#3b82f6",
                    "Female Only": "#ec4899",
                },
            )
            fig_sun.update_layout(height=380)
            st.plotly_chart(fig_sun, use_container_width=True)

        st.divider()
        r2c1, r2c2 = st.columns(2)
        with r2c1:
            st.subheader("📍 Average Monthly Rent by Locality")
            area_stats = (
                fdf.groupby("Location")
                .agg(AvgCost=("Cost", "mean"), Count=("Name", "count"), AvgRating=("Rating", "mean"))
                .reset_index()
                .sort_values("AvgCost", ascending=True)
            )
            fig_bar = px.bar(
                area_stats,
                x="AvgCost",
                y="Location",
                orientation="h",
                color="AvgRating",
                color_continuous_scale="Viridis",
                hover_data=["Count"],
                text_auto=".0f",
                labels={"AvgCost": "Average Rent (₹)", "Location": "Locality", "AvgRating": "Avg Rating"},
            )
            fig_bar.update_layout(height=420)
            st.plotly_chart(fig_bar, use_container_width=True)

        with r2c2:
            st.subheader("📦 Rent Spread & Outliers by Top Localities")
            top_locs = fdf["Location"].value_counts().head(10).index.tolist()
            box_df = fdf[fdf["Location"].isin(top_locs)]
            fig_box = px.box(
                box_df,
                x="Location",
                y="Cost",
                color="Location",
                points="all",
                hover_data=["Name", "Sharing", "PGType"],
                labels={"Cost": "Monthly Rent (₹)", "Location": "Locality"},
            )
            fig_box.update_layout(height=420, showlegend=False)
            st.plotly_chart(fig_box, use_container_width=True)

        st.divider()
        r3c1, r3c2 = st.columns(2)
        with r3c1:
            st.subheader("🎯 Price vs. Rating Matrix (Bubble Size = Food Quality)")
            if not rated_pgs.empty:
                scatter_df = rated_pgs.copy()
                scatter_df["BubbleSize"] = scatter_df["FoodRating"].clip(lower=1.0) * 4
                fig_scat = px.scatter(
                    scatter_df,
                    x="Cost",
                    y="Rating",
                    color="PGType",
                    size="BubbleSize",
                    hover_name="Name",
                    hover_data=["Location", "Sharing", "FoodRating", "ValueScore", "Electricity"],
                    color_discrete_map={
                        "Co-Living": "#6366f1",
                        "Male Only": "#3b82f6",
                        "Female Only": "#ec4899",
                    },
                    labels={"Cost": "Monthly Rent (₹)", "Rating": "Overall Rating (1-5)"},
                )
                fig_scat.update_layout(height=400)
                st.plotly_chart(fig_scat, use_container_width=True)
            else:
                st.info("No rated PGs available for scatter visualization.")

        with r3c2:
            st.subheader("🏢 Room Space vs. Monthly Rent & Food Quality")
            space_order = ["Spacious", "Average", "Cramped"]
            fig_space = px.violin(
                fdf,
                x="RoomSpace",
                y="Cost",
                color="RoomSpace",
                box=True,
                points="all",
                category_orders={"RoomSpace": space_order},
                hover_data=["Name", "Location", "Sharing"],
                labels={"RoomSpace": "Room Space Perception", "Cost": "Monthly Rent (₹)"},
            )
            fig_space.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_space, use_container_width=True)

        st.divider()
        st.subheader("🏆 Top 10 Value-for-Money PGs (Rating² / Cost × 5000)")
        if not rated_pgs.empty:
            top_value = rated_pgs.sort_values(["ValueScore", "Rating", "FoodRating"], ascending=[False, False, False]).head(10)
            st.dataframe(
                top_value[
                    [
                        "Name",
                        "Location",
                        "PGType",
                        "Sharing",
                        "Cost",
                        "Rating",
                        "FoodRating",
                        "ValueScore",
                        "Electricity",
                        "SmartTags",
                        "Phone",
                    ]
                ],
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Cost": st.column_config.NumberColumn("Monthly Rent", format="₹%d"),
                    "Rating": st.column_config.NumberColumn("Overall Rating", format="%.1f ⭐"),
                    "FoodRating": st.column_config.NumberColumn("Food Quality", format="%.1f 🍴"),
                    "ValueScore": st.column_config.ProgressColumn(
                        "Value Score",
                        format="%.2f",
                        min_value=0,
                        max_value=float(max(15.0, df_all["ValueScore"].max())),
                    ),
                },
            )


# ══════════════════════════════════════════════
#  PAGE 2: INTERACTIVE METRO & COMMUTE MAP
# ══════════════════════════════════════════════
elif page == "🚇 Metro & Commute Map":
    st.title("🚇 Interactive Geospatial Map & IT Hub Commute Planner")
    st.markdown(
        "Visualize every PG alongside **Hyderabad Metro stations (Blue, Red, Green Lines)** and calculate "
        "commute proximity to your office hub."
    )

    if df_all.empty:
        st.stop()

    mcol1, mcol2, mcol3, mcol4 = st.columns([1.4, 1.0, 1.0, 1.0])
    with mcol1:
        work_hub = st.selectbox("🏢 Select Your Office / IT Hub", list(IT_HUBS.keys()))
    with mcol2:
        max_commute_km = st.slider("🚗 Max Distance to Hub (km)", 1.0, 25.0, 8.0, 0.5)
    with mcol3:
        map_pg_type = st.selectbox("👥 Filter PG Type", ["Any", "Male Only", "Female Only", "Co-Living"])
    with mcol4:
        color_mode = st.selectbox("🎨 Color Map Pins By", ["Monthly Rent (₹)", "Overall Rating", "PG Type"])

    hub_lat, hub_lon = IT_HUBS[work_hub]
    mdf = df_all.copy()
    mdf["HubDistKm"] = mdf.apply(
        lambda r: round(haversine_km(r["lat"], r["lon"], hub_lat, hub_lon), 1),
        axis=1,
    )
    if map_pg_type != "Any":
        mdf = mdf[mdf["PGType"] == map_pg_type]
    nearby_df = mdf[mdf["HubDistKm"] <= max_commute_km].sort_values(["HubDistKm", "ValueScore"], ascending=[True, False])

    # ── BUILD INTERACTIVE PLOTLY MAPBOX ──
    color_col = {"Monthly Rent (₹)": "Cost", "Overall Rating": "Rating", "PG Type": "PGType"}[color_mode]
    fig_map = px.scatter_mapbox(
        mdf,
        lat="lat",
        lon="lon",
        color=color_col,
        hover_name="Name",
        hover_data={
            "Location": True,
            "PGType": True,
            "Sharing": True,
            "Cost": ":₹,.0f",
            "Rating": ":.1f",
            "FoodRating": ":.1f",
            "NearestMetro": True,
            "MetroDistKm": True,
            "HubDistKm": True,
            "Phone": True,
            "lat": False,
            "lon": False,
        },
        zoom=11.2,
        center={"lat": hub_lat, "lon": hub_lon},
        height=560,
        mapbox_style="carto-positron",
        color_continuous_scale="Plasma" if color_col == "Cost" else "Viridis",
    )
    fig_map.update_traces(marker=dict(size=11, opacity=0.88))

    # Overlay Metro Lines & Stations
    metro_df = pd.DataFrame(METRO_STATIONS)
    line_colors = {"Blue Line": "#2563eb", "Red Line": "#dc2626", "Green Line": "#16a34a"}
    for line_name, ldf in metro_df.groupby("line", sort=False):
        fig_map.add_trace(
            go.Scattermapbox(
                lat=ldf["lat"],
                lon=ldf["lon"],
                mode="lines+markers",
                name=f"🚇 {line_name}",
                line=dict(width=3, color=line_colors.get(line_name, "#2563eb")),
                marker=dict(size=8, color=line_colors.get(line_name, "#2563eb")),
                text=ldf["station"] + " Metro (" + ldf["line"] + ")",
                hoverinfo="text",
            )
        )

    # Overlay Selected Workplace Hub
    fig_map.add_trace(
        go.Scattermapbox(
            lat=[hub_lat],
            lon=[hub_lon],
            mode="markers+text",
            name=f"🏢 {work_hub}",
            marker=dict(size=18, color="#111827"),
            text=[f"🏢 {work_hub}"],
            textposition="top right",
            hoverinfo="text",
        )
    )

    fig_map.update_layout(margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", yanchor="bottom", y=1.01))
    st.plotly_chart(fig_map, use_container_width=True)

    # ── COMMUTE PLANNER RESULTS ──
    st.subheader(f"📍 PGs within {max_commute_km:.1f} km of {work_hub} ({len(nearby_df)} matches)")
    if nearby_df.empty:
        st.info("No PGs found within this distance radius. Try increasing the max distance slider above.")
    else:
        st.dataframe(
            nearby_df[
                [
                    "Name",
                    "Location",
                    "HubDistKm",
                    "NearestMetro",
                    "MetroDistKm",
                    "PGType",
                    "Sharing",
                    "Cost",
                    "Rating",
                    "FoodRating",
                    "ValueScore",
                    "SmartTags",
                    "Phone",
                    "MapsURL",
                ]
            ],
            hide_index=True,
            use_container_width=True,
            column_config={
                "HubDistKm": st.column_config.NumberColumn("Dist to Office", format="%.1f km"),
                "NearestMetro": st.column_config.TextColumn("Nearest Metro"),
                "MetroDistKm": st.column_config.NumberColumn("Metro Dist", format="%.1f km"),
                "Cost": st.column_config.NumberColumn("Rent / Mo", format="₹%d"),
                "Rating": st.column_config.NumberColumn("Rating", format="%.1f ⭐"),
                "FoodRating": st.column_config.NumberColumn("Food", format="%.1f 🍴"),
                "ValueScore": st.column_config.NumberColumn("Value Score", format="%.2f"),
                "MapsURL": st.column_config.LinkColumn("Map", display_text="📍 Open Map"),
            },
        )

    st.divider()
    c_metro1, c_metro2 = st.columns([2, 1])
    with c_metro1:
        st.markdown(
            """
            ### 🚆 Hyderabad Metro Core Corridors
            * **🔵 Blue Line (Raidurg ↔ Nagole):** Connects the Western IT Corridor (*Raidurg, HITEC City, Durgam Cheruvu, Madhapur, Jubilee Hills*) with *Ameerpet, Begumpet, Secunderabad, Uppal,* and *Nagole*.
            * **🔴 Red Line (Miyapur ↔ LB Nagar):** Connects residential hubs (*Miyapur, JNTU, KPHB, Kukatpally, SR Nagar, Ameerpet*) with *Punjagutta, Narayanguda/MGBS, Dilsukhnagar,* and *LB Nagar*.
            * **🟢 Green Line (JBS Parade Ground ↔ MGBS):** Connects *Secunderabad/Parade Ground, RTC X Roads, Narayanguda,* and *MG Bus Station*.
            """
        )
    with c_metro2:
        st.markdown("### 🗺️ Official Transit Map")
        st.write("Check live L&T Hyderabad Metro timings, fare charts, and station facilities:")
        st.link_button("Launch Official L&T Metro Map", "https://ltmetro.com/metro-network-map/", use_container_width=True)


# ══════════════════════════════════════════════
#  PAGE 3: ADD A PG & COMMUNITY INFO
# ══════════════════════════════════════════════
elif page == "➕ Add a PG & Community Info":
    st.title("🤝 The Story Behind the r/hyderabad PG Directory")

    st.markdown(
        """
        Finding a reliable PG in Hyderabad can be daunting. Between inflated broker fees, misleading listing photos,
        unreturned security deposits, and hidden electricity charges, newcomers often struggle to find honest information.

        To fix this, the **r/hyderabad** community came together to build a transparent, crowdsourced database of PG and Co-Living stays:

        * **How it started:** Sparked by [this original r/hyderabad thread](https://www.reddit.com/r/hyderabad/comments/1mzjwfj/lets_build_the_ultimate_hyderabad_pg_database/), residents began sharing honest reviews, real rents, food quality ratings, and direct owner contacts.
        * **How it evolved:** The static spreadsheet grew into this live analytics dashboard, launched in [this follow-up community post](https://www.reddit.com/r/hyderabad/comments/1ppxvnz/i_built_a_live_dashboard_to_find_pgs_in_hyderabad/).

        **100% Community-Driven:** Zero brokers, zero sponsored listings, and full transparency.
        """
    )

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📝 Submit Your PG Review")
        st.write(
            "Help the next person moving to Hyderabad! Share your current or past PG's rent, food rating, "
            "pros & cons, and owner contact via the official Google Form (auto-syncs with this dashboard)."
        )
        st.link_button(
            "🚀 Launch PG Submission Form",
            "https://docs.google.com/forms/d/e/1FAIpQLScXRf8vHeXwMeAbY_QLGDjGYemxD6BClUGffeOTTcra_9IBcQ/viewform",
            use_container_width=True,
        )

    with col2:
        st.subheader("📂 Public Google Sheet & Reddit Threads")
        st.write("Want to inspect the raw crowdsourced responses or run your own analysis?")
        st.link_button(
            "📊 Open Master Google Sheet",
            "https://docs.google.com/spreadsheets/d/1AW4EKm412u_UyYhf1swdhDsP5ikadr3XXeUTMrqvh4w/edit",
            use_container_width=True,
        )
        st.markdown(
            """
            * [Reddit Thread Part 1: Let's build the ultimate Hyderabad PG database!](https://www.reddit.com/r/hyderabad/comments/1mzjwfj/lets_build_the_ultimate_hyderabad_pg_database/)
            * [Reddit Thread Part 2: I built a live dashboard to find PGs in Hyderabad](https://www.reddit.com/r/hyderabad/comments/1ppxvnz/i_built_a_live_dashboard_to_find_pgs_in_hyderabad/)
            """
        )

    if not df_all.empty:
        st.divider()
        rcol1, rcol2 = st.columns([1.6, 1.0])
        with rcol1:
            st.subheader("🕒 Latest Community Submissions")
            recent_df = df_all.sort_values("SubmittedAt", ascending=False, na_position="last").head(8)
            st.dataframe(
                recent_df[["Name", "Location", "PGType", "Sharing", "Cost", "Rating", "FoodRating", "Contributor"]],
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Cost": st.column_config.NumberColumn("Rent", format="₹%d"),
                    "Rating": st.column_config.NumberColumn("Rating", format="%.1f ⭐"),
                    "FoodRating": st.column_config.NumberColumn("Food", format="%.1f 🍴"),
                },
            )
        with rcol2:
            st.subheader("🏅 Top Community Contributors")
            named_contribs = df_all[df_all["Contributor"].str.lower() != "anonymous"]["Contributor"].value_counts().head(10).reset_index()
            named_contribs.columns = ["Reddit Username", "Reviews Submitted"]
            if not named_contribs.empty:
                st.dataframe(named_contribs, hide_index=True, use_container_width=True)
            else:
                st.caption("Most contributors chose to remain Anonymous.")
