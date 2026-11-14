import html
import math
import os
import re
from datetime import datetime
from io import StringIO
from urllib.parse import quote_plus

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Hyderabad PG Directory — Community Reviews & Rent Intelligence",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)


def render_html(raw_html: str) -> None:
    """
    Renders multi-line HTML safely in Streamlit by collapsing line breaks and
    indentation so CommonMark never splits an HTML block into a code block.
    """
    compact = " ".join(line.strip() for line in raw_html.splitlines() if line.strip())
    st.markdown(compact, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  DESIGN SYSTEM & CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1380px;
    }
    .masthead {
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 14px;
        padding: 1.3rem 1.55rem;
        margin-bottom: 1.2rem;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.04) 0%, rgba(15, 23, 42, 0.01) 100%);
    }
    .masthead-top {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        flex-wrap: wrap;
        gap: 1rem;
    }
    .masthead-title {
        font-size: 1.5rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin: 0 0 0.28rem 0;
        line-height: 1.25;
    }
    .masthead-sub {
        font-size: 0.91rem;
        opacity: 0.78;
        margin: 0;
        max-width: 760px;
        line-height: 1.45;
    }
    .masthead-actions {
        display: flex;
        gap: 0.55rem;
        flex-wrap: wrap;
        align-items: center;
    }
    .btn-outline, .btn-primary {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.42rem 0.88rem;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 600;
        text-decoration: none !important;
        transition: all 0.15s ease;
    }
    .btn-primary {
        background-color: #2563eb;
        color: #ffffff !important;
        border: 1px solid #1d4ed8;
    }
    .btn-primary:hover {
        background-color: #1d4ed8;
    }
    .btn-outline {
        background-color: rgba(148, 163, 184, 0.1);
        color: inherit !important;
        border: 1px solid rgba(148, 163, 184, 0.32);
    }
    .btn-outline:hover {
        background-color: rgba(148, 163, 184, 0.18);
    }
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
        gap: 0.85rem;
        margin-bottom: 1.2rem;
    }
    .kpi-box {
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 10px;
        padding: 0.85rem 1.05rem;
        background-color: rgba(148, 163, 184, 0.03);
    }
    .kpi-label {
        font-size: 0.74rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        opacity: 0.68;
        font-weight: 600;
        margin-bottom: 0.22rem;
    }
    .kpi-val {
        font-size: 1.32rem;
        font-weight: 700;
        letter-spacing: -0.01em;
        line-height: 1.2;
    }
    .kpi-sub {
        font-size: 0.78rem;
        opacity: 0.72;
        margin-top: 0.2rem;
    }
    .prop-card {
        border: 1px solid rgba(148, 163, 184, 0.26);
        border-radius: 12px;
        padding: 1.25rem 1.4rem;
        margin-bottom: 0.95rem;
        background-color: rgba(148, 163, 184, 0.025);
        transition: border-color 0.15s ease;
    }
    .prop-card:hover {
        border-color: rgba(59, 130, 246, 0.5);
    }
    .prop-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 1rem;
        flex-wrap: wrap;
        margin-bottom: 0.65rem;
    }
    .prop-name {
        font-size: 1.14rem;
        font-weight: 700;
        margin: 0 0 0.35rem 0;
        letter-spacing: -0.01em;
    }
    .prop-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        align-items: center;
        font-size: 0.82rem;
        opacity: 0.88;
    }
    .prop-price-block {
        text-align: right;
        min-width: 145px;
    }
    .prop-price {
        font-size: 1.3rem;
        font-weight: 700;
        color: #10b981;
        line-height: 1.15;
    }
    .prop-price-unit {
        font-size: 0.78rem;
        font-weight: 500;
        opacity: 0.75;
    }
    .prop-elec {
        font-size: 0.75rem;
        margin-top: 0.2rem;
        font-weight: 500;
    }
    .elec-inc {
        color: #10b981;
    }
    .elec-sep {
        color: #f59e0b;
    }
    .badge {
        display: inline-block;
        padding: 0.16rem 0.55rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        line-height: 1.3;
    }
    .badge-area {
        background-color: rgba(59, 130, 246, 0.14);
        color: #3b82f6;
        border: 1px solid rgba(59, 130, 246, 0.28);
    }
    .badge-male {
        background-color: rgba(14, 165, 233, 0.13);
        color: #0ea5e9;
        border: 1px solid rgba(14, 165, 233, 0.28);
    }
    .badge-female {
        background-color: rgba(236, 72, 153, 0.13);
        color: #ec4899;
        border: 1px solid rgba(236, 72, 153, 0.28);
    }
    .badge-colive {
        background-color: rgba(139, 92, 246, 0.13);
        color: #8b5cf6;
        border: 1px solid rgba(139, 92, 246, 0.28);
    }
    .badge-neutral {
        background-color: rgba(148, 163, 184, 0.14);
        border: 1px solid rgba(148, 163, 184, 0.28);
    }
    .specs-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem 1.2rem;
        padding: 0.55rem 0.8rem;
        border-radius: 8px;
        background-color: rgba(148, 163, 184, 0.06);
        margin: 0.6rem 0;
        font-size: 0.81rem;
    }
    .spec-item {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
    }
    .spec-label {
        opacity: 0.68;
    }
    .spec-val {
        font-weight: 600;
    }
    .tag-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.4rem;
        margin: 0.55rem 0;
    }
    .tag-pos {
        padding: 0.15rem 0.55rem;
        border-radius: 999px;
        font-size: 0.74rem;
        font-weight: 500;
        background-color: rgba(16, 185, 129, 0.11);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.28);
    }
    .tag-warn {
        padding: 0.15rem 0.55rem;
        border-radius: 999px;
        font-size: 0.74rem;
        font-weight: 600;
        background-color: rgba(239, 68, 68, 0.12);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.32);
    }
    .review-box {
        font-size: 0.89rem;
        line-height: 1.55;
        padding: 0.65rem 0.9rem;
        border-left: 3px solid rgba(59, 130, 246, 0.45);
        background-color: rgba(148, 163, 184, 0.04);
        border-radius: 0 8px 8px 0;
        margin: 0.65rem 0;
    }
    .prop-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.6rem;
        padding-top: 0.55rem;
        border-top: 1px solid rgba(148, 163, 184, 0.15);
        font-size: 0.78rem;
    }
    .prop-credit {
        opacity: 0.68;
    }
    .prop-links {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    .card-link {
        display: inline-block;
        padding: 0.28rem 0.68rem;
        border-radius: 6px;
        font-size: 0.77rem;
        font-weight: 600;
        text-decoration: none !important;
        border: 1px solid rgba(148, 163, 184, 0.32);
        background-color: rgba(148, 163, 184, 0.08);
        color: inherit !important;
    }
    .card-link:hover {
        border-color: #3b82f6;
        color: #3b82f6 !important;
    }
    .card-link-wa {
        border-color: rgba(16, 185, 129, 0.4);
        background-color: rgba(16, 185, 129, 0.1);
        color: #10b981 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
#  CONSTANTS & GEOSPATIAL REFERENCE DATA
# ─────────────────────────────────────────────────────────────────────────────
SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1AW4EKm412u_UyYhf1swdhDsP5ikadr3XXeUTMrqvh4w/export?format=csv&gid=1856698473"
)
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScXRf8vHeXwMeAbY_QLGDjGYemxD6BClUGffeOTTcra_9IBcQ/viewform"
SHEET_EDIT_URL = "https://docs.google.com/spreadsheets/d/1AW4EKm412u_UyYhf1swdhDsP5ikadr3XXeUTMrqvh4w/edit"
LOCAL_CSV_PATH = os.path.join(os.path.dirname(__file__), "pg_data.csv")

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

OFFICE_HUBS = {
    "None (All Hyderabad)": None,
    "Mindspace / Raheja IT Park (HITEC City)": (17.4422, 78.3774),
    "DLF Cyber City / Gachibowli": (17.4485, 78.3548),
    "Financial District / WaveRock / Nanakramguda": (17.4158, 78.3426),
    "Knowledge City / Raidurg / T-Hub": (17.4344, 78.3827),
    "Kondapur / Botanical Garden Rd": (17.4567, 78.3522),
    "Kokapet SEZ / GAR Infobahn": (17.3926, 78.3321),
    "Ameerpet / Begumpet Commercial Hub": (17.4399, 78.4563),
    "Pocharam / Infosys SEZ": (17.4418, 78.6472),
    "Adibatla / TCS SEZ": (17.2321, 78.5624),
}

METRO_STATIONS = [
    {"station": "Raidurg", "line": "Blue Line", "lat": 17.4422, "lon": 78.3774},
    {"station": "HITEC City", "line": "Blue Line", "lat": 17.4489, "lon": 78.3832},
    {"station": "Durgam Cheruvu", "line": "Blue Line", "lat": 17.4428, "lon": 78.3875},
    {"station": "Madhapur", "line": "Blue Line", "lat": 17.4372, "lon": 78.3983},
    {"station": "Peddamma Gudi", "line": "Blue Line", "lat": 17.4306, "lon": 78.4083},
    {"station": "Jubilee Hills Check Post", "line": "Blue Line", "lat": 17.4265, "lon": 78.4198},
    {"station": "Ameerpet", "line": "Blue Line", "lat": 17.4357, "lon": 78.4446},
    {"station": "Begumpet", "line": "Blue Line", "lat": 17.4439, "lon": 78.4607},
    {"station": "Secunderabad East", "line": "Blue Line", "lat": 17.4354, "lon": 78.5046},
    {"station": "Uppal", "line": "Blue Line", "lat": 17.4002, "lon": 78.5601},
    {"station": "Nagole", "line": "Blue Line", "lat": 17.3908, "lon": 78.5594},
    {"station": "Miyapur", "line": "Red Line", "lat": 17.4967, "lon": 78.3731},
    {"station": "JNTU College", "line": "Red Line", "lat": 17.4986, "lon": 78.3888},
    {"station": "KPHB Colony", "line": "Red Line", "lat": 17.4938, "lon": 78.4017},
    {"station": "Kukatpally", "line": "Red Line", "lat": 17.4851, "lon": 78.4095},
    {"station": "SR Nagar", "line": "Red Line", "lat": 17.4440, "lon": 78.4414},
    {"station": "Punjagutta", "line": "Red Line", "lat": 17.4286, "lon": 78.4510},
    {"station": "MGBS", "line": "Red Line", "lat": 17.3788, "lon": 78.4800},
    {"station": "Dilsukhnagar", "line": "Red Line", "lat": 17.3685, "lon": 78.5257},
    {"station": "Chaitanyapuri", "line": "Red Line", "lat": 17.3682, "lon": 78.5361},
    {"station": "LB Nagar", "line": "Red Line", "lat": 17.3457, "lon": 78.5522},
    {"station": "JBS Parade Ground", "line": "Green Line", "lat": 17.4437, "lon": 78.4973},
    {"station": "RTC X Roads", "line": "Green Line", "lat": 17.4072, "lon": 78.4966},
    {"station": "Narayanguda", "line": "Green Line", "lat": 17.3944, "lon": 78.4900},
]


# ─────────────────────────────────────────────────────────────────────────────
#  DATA CLEANING & ENRICHMENT ENGINE
# ─────────────────────────────────────────────────────────────────────────────
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def clean_cost(val) -> float:
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
    if pd.isna(raw_type):
        return "Co-Living"
    low = str(raw_type).lower()
    if "co living" in low or "coliving" in low or "both" in low:
        return "Co-Living"
    if "female" in low or "women" in low or "ladies" in low or "girl" in low:
        return "Women's PG"
    if "male" in low or "men" in low or "boy" in low or "gents" in low:
        return "Men's PG"
    return "Co-Living"


def normalize_parking(raw_parking) -> str:
    if pd.isna(raw_parking) or not str(raw_parking).strip():
        return "Not Specified"
    low = str(raw_parking).lower()
    if "no parking" in low and "infront" not in low and "front" not in low:
        return "No Parking"
    if "4-wheeler" in low or "4 wheeler" in low or "four wheeler" in low or "both" in low or "spacious" in low:
        return "2 & 4 Wheeler"
    if "congested" in low or "less space" in low:
        return "2-Wheeler (Tight)"
    if "front" in low or "empty site" in low or "outside" in low:
        return "Street / Outside"
    if "2-wheeler" in low or "2 wheeler" in low:
        return "2-Wheeler"
    return "2-Wheeler"


def clean_phone(raw_phone) -> tuple[str, str]:
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


def extract_highlights_and_warnings(row: pd.Series) -> tuple[list[str], list[str]]:
    text = str(row.get("Comments", "")).lower()
    pos, warn = [], []

    if any(w in text for w in ["slow wifi", "slow wi-fi", "wifi is slow", "wi-fi speed can be slow", "wifi speed low", "ping is shit"]):
        warn.append("Slow Wi-Fi")
    elif any(w in text for w in ["wifi", "wi-fi", "internet"]):
        pos.append("Reliable Wi-Fi")

    if any(w in text for w in ["metro", "bus stop", "public transport", "walkable", "walking distance"]):
        pos.append("Walkable to Transit")

    if "no gym" not in text and any(w in text for w in ["gym", "fitness"]):
        pos.append("Gym")
    if "no game" not in text and any(w in text for w in ["pool table", "indoor games", "gaming zone", "box cricket", "play area"]):
        pos.append("Recreation Area")
    if any(w in text for w in [" ac ", " ac,", "ac room", "air condition", "fully furnished with ac", "ac 2", "ac 3"]):
        pos.append("AC Available")
    if any(w in text for w in ["washing machine", "laundry"]):
        pos.append("Washing Machine")
    if any(w in text for w in ["power backup", "inverter", "generator"]):
        pos.append("Power Backup")
    if any(w in text for w in ["fridge", "self kitchen", "self cooking", "cook your own", "induction"]):
        pos.append("Fridge / Self-Cook")
    if any(w in text for w in ["cctv", "fingerprint", "biometric", "security guard", "security uncle", "access card"]):
        pos.append("Biometric / CCTV")
    if any(w in text for w in ["clean daily", "daily cleaning", "very neat", "hygenic", "cleaned every"]):
        pos.append("Regular Housekeeping")

    if any(w in text for w in ["bed bug", "bedbug", "cockroach", "insects", "pest", "rot"]):
        warn.append("Pest / Hygiene Issue")
    if any(w in text for w in ["rude", "horrible", "not give back the advance", "micromanager", "trash"]):
        warn.append("Management / Deposit Warning")
    if any(w in text for w in ["no power backup", "lift keeps getting stuck", "turn off the lift"]):
        warn.append("Lift / Backup Issue")
    if any(w in text for w in ["signal", "network"]):
        warn.append("Weak Mobile Network")

    return pos, warn


@st.cache_data(ttl=600, show_spinner="Loading Hyderabad PG directory...")
def load_data() -> tuple[pd.DataFrame, str]:
    source_label = "Live Google Sheet"
    try:
        resp = requests.get(SHEET_CSV_URL, timeout=6)
        resp.raise_for_status()
        raw_df = pd.read_csv(StringIO(resp.text), dtype={"PG Owner Phone number": str})
    except Exception:
        source_label = "Local CSV Snapshot"
        if os.path.exists(LOCAL_CSV_PATH):
            raw_df = pd.read_csv(LOCAL_CSV_PATH, dtype={"PG Owner Phone number": str})
        else:
            return pd.DataFrame(), "Offline"

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

    df["Name"] = df["Name"].fillna("Unnamed PG").astype(str).str.strip()
    df["Cost"] = df["Cost"].apply(clean_cost)
    df = df[(df["Cost"] >= 2000) & (df["Cost"] <= 65000)].copy()

    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce").fillna(0.0).clip(0.0, 5.0)
    df["FoodRating"] = pd.to_numeric(df["FoodRating"], errors="coerce").fillna(0.0).clip(0.0, 5.0)

    loc_parsed = df["LocationRaw"].apply(normalize_location)
    df["Location"] = [item[0] for item in loc_parsed]
    df["ExtraMapURL"] = [item[1] for item in loc_parsed]

    df["PGType"] = df["PGTypeRaw"].apply(normalize_pg_type)
    df["Sharing"] = df["Sharing"].fillna("Unknown").astype(str).str.strip()
    df["RoomSpace"] = df["RoomSpace"].fillna("Average").astype(str).str.strip()
    df["Electricity"] = df["Electricity"].fillna("Included in rent").astype(str).str.strip()
    df["ParkingRaw"] = df["ParkingRaw"].fillna("Not specified").astype(str).str.strip()
    df["ParkingCategory"] = df["ParkingRaw"].apply(normalize_parking)

    # Estimated True Monthly Cost (adds ~₹800/mo buffer when electricity is billed separately)
    df["EstTotalCost"] = np.where(df["Electricity"] == "Separate bill", df["Cost"] + 800, df["Cost"])

    df["Comments"] = df["Comments"].fillna("").astype(str).str.strip()
    df["Contributor"] = df["Contributor"].fillna("Anonymous").astype(str).str.strip().replace({"": "Anonymous"})
    df["SubmittedAt"] = pd.to_datetime(df.get("Timestamp"), errors="coerce")

    phone_parsed = df["PhoneRaw"].apply(clean_phone)
    df["Phone"] = [item[0] for item in phone_parsed]
    df["PhoneDigits"] = [item[1] for item in phone_parsed]

    hw_parsed = df.apply(extract_highlights_and_warnings, axis=1)
    df["Highlights"] = [item[0] for item in hw_parsed]
    df["Warnings"] = [item[1] for item in hw_parsed]
    df["HighlightsStr"] = df["Highlights"].apply(lambda x: ", ".join(x) if x else "—")
    df["WarningsStr"] = df["Warnings"].apply(lambda x: ", ".join(x) if x else "None")

    # Composite Quality Score (70% Overall Rating + 30% Food Quality)
    df["CompositeRating"] = np.where(
        df["FoodRating"] > 0,
        (df["Rating"] * 0.7 + df["FoodRating"] * 0.3).round(2),
        df["Rating"],
    )

    # Sharing-Adjusted Value Score (compares rent against the median rent of the SAME sharing tier)
    sharing_medians = df.groupby("Sharing")["EstTotalCost"].transform("median")
    relative_cost_ratio = (df["EstTotalCost"] / sharing_medians).clip(0.5, 2.0)
    df["ValueScore"] = ((df["CompositeRating"] / relative_cost_ratio) * 2.0).round(2)

    # Smart Recommendation Rank Score (prioritizes high ratings, fair value, detailed reviews, and verified phone)
    has_review_bonus = np.where(df["Comments"].str.len() >= 25, 1.2, 0.0)
    has_phone_bonus = np.where(df["PhoneDigits"] != "", 0.5, 0.0)
    warning_penalty = df["Warnings"].apply(lambda w: 1.5 if len(w) > 0 else 0.0)
    df["RecScore"] = (df["ValueScore"] + has_review_bonus + has_phone_bonus - warning_penalty).round(2)

    # Locality Coordinates + Deterministic Offset for Map Display
    rng = np.random.default_rng(42)
    base_coords = df["Location"].map(lambda loc: COORDS.get(loc, COORDS["Unknown"]))
    df["AreaLat"] = [c[0] for c in base_coords]
    df["AreaLon"] = [c[1] for c in base_coords]
    df["lat"] = df["AreaLat"] + rng.normal(0, 0.0024, len(df))
    df["lon"] = df["AreaLon"] + rng.normal(0, 0.0024, len(df))

    # Nearest Metro Station from Locality Center
    nearest_names, nearest_lines, nearest_dists = [], [], []
    for _, row in df.iterrows():
        best_st = min(
            METRO_STATIONS,
            key=lambda st_item: haversine_km(row["AreaLat"], row["AreaLon"], st_item["lat"], st_item["lon"]),
        )
        dist = haversine_km(row["AreaLat"], row["AreaLon"], best_st["lat"], best_st["lon"])
        nearest_names.append(best_st["station"])
        nearest_lines.append(best_st["line"])
        nearest_dists.append(round(dist, 1))

    df["NearestMetro"] = nearest_names
    df["MetroLine"] = nearest_lines
    df["MetroDistKm"] = nearest_dists

    df["MapsURL"] = df.apply(
        lambda r: r["ExtraMapURL"]
        if r["ExtraMapURL"]
        else f"https://www.google.com/maps/search/?api=1&query={quote_plus(str(r['Name']) + ' ' + str(r['Location']) + ' Hyderabad')}",
        axis=1,
    )

    return df.reset_index(drop=True), source_label


def get_monthly_users() -> int:
    namespace = "hyderabad_pg_directory_reddit"
    current_month = datetime.now().strftime("%Y_%m")
    counter_name = f"monthly_users_{current_month}"
    api_url = f"https://api.counterapi.dev/v1/{namespace}/{counter_name}"

    if "view_logged" not in st.session_state:
        st.session_state.view_logged = True
        try:
            response = requests.get(f"{api_url}/up", timeout=2.0)
            if response.status_code == 200:
                st.session_state.current_monthly_users = response.json().get("count", 0)
        except Exception:
            st.session_state.current_monthly_users = st.session_state.get("current_monthly_users", 0)
    return st.session_state.get("current_monthly_users", 0)


# ─────────────────────────────────────────────────────────────────────────────
#  LOAD DATA & SIDEBAR FILTER PANEL
# ─────────────────────────────────────────────────────────────────────────────
df_all, data_source = load_data()
monthly_users = get_monthly_users()

if df_all.empty:
    st.error("Unable to load the PG directory dataset. Please verify your internet connection or local `pg_data.csv`.")
    st.stop()

with st.sidebar:
    st.markdown("### Search & Filter PGs")
    st.caption("Narrow down listings by commute hub, neighborhood, room type, and budget.")

    search_query = st.text_input(
        "Keyword Search",
        placeholder="PG name, landmark, Deloitte, AC, gym...",
        help="Searches across PG names, localities, and full review comments.",
    )

    sel_hub = st.selectbox(
        "Commuting To (Office Hub)",
        options=list(OFFICE_HUBS.keys()),
        index=0,
        help="Calculates straight-line distance from each PG's locality to your workplace.",
    )
    max_hub_km = None
    if OFFICE_HUBS[sel_hub] is not None:
        max_hub_km = st.slider("Max Distance to Office (km)", 1.0, 25.0, 8.0, 0.5)

    all_locs = sorted(df_all["Location"].unique().tolist())
    sel_locs = st.multiselect("Localities", all_locs, default=[], placeholder="All Localities")

    sel_pg_type = st.selectbox(
        "Accommodation Type",
        ["All Types", "Men's PG", "Women's PG", "Co-Living"],
    )

    sharing_order = ["Single", "Two Sharing", "Triple Sharing", "Four Sharing", "Five Sharing"]
    avail_sharing = [s for s in sharing_order if s in df_all["Sharing"].unique()]
    sel_sharing = st.multiselect("Room Sharing", avail_sharing, default=[], placeholder="Any Sharing")

    min_c = int(df_all["Cost"].min() // 500 * 500)
    max_c = int(math.ceil(df_all["Cost"].max() / 500.0) * 500)
    max_budget = st.slider(
        "Max Monthly Rent (₹)",
        min_value=min_c,
        max_value=max_c,
        value=min(25000, max_c),
        step=500,
    )

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        min_rating = st.selectbox("Min Rating", [0.0, 3.0, 3.5, 4.0, 4.5], format_func=lambda x: "Any" if x == 0 else f"{x}+ ★")
    with col_r2:
        min_food = st.selectbox("Min Food", [0.0, 3.0, 4.0], format_func=lambda x: "Any" if x == 0 else f"{x}+ ★")

    st.markdown("**Preferences**")
    only_elec_inc = st.checkbox("Electricity included in rent", value=False)
    only_4w_parking = st.checkbox("4-Wheeler parking available", value=False)
    hide_warnings = st.checkbox("Exclude listings with pest/deposit warnings", value=False)

    st.divider()
    scol_a, scol_b = st.columns(2)
    with scol_a:
        st.caption(f"**Source:** {data_source}")
        if monthly_users > 0:
            st.caption(f"**Monthly Visits:** {monthly_users:,}")
    with scol_b:
        if st.button("Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
#  APPLY FILTERS & COMMUTE CALCULATIONS
# ─────────────────────────────────────────────────────────────────────────────
fdf = df_all.copy()

if OFFICE_HUBS[sel_hub] is not None:
    h_lat, h_lon = OFFICE_HUBS[sel_hub]
    fdf["OfficeDistKm"] = fdf.apply(
        lambda r: round(haversine_km(r["AreaLat"], r["AreaLon"], h_lat, h_lon), 1),
        axis=1,
    )
    if max_hub_km is not None:
        fdf = fdf[fdf["OfficeDistKm"] <= max_hub_km]
else:
    fdf["OfficeDistKm"] = np.nan

if sel_locs:
    fdf = fdf[fdf["Location"].isin(sel_locs)]
if sel_pg_type != "All Types":
    fdf = fdf[fdf["PGType"] == sel_pg_type]
if sel_sharing:
    fdf = fdf[fdf["Sharing"].isin(sel_sharing)]

fdf = fdf[fdf["Cost"] <= max_budget]
if min_rating > 0:
    fdf = fdf[fdf["Rating"] >= min_rating]
if min_food > 0:
    fdf = fdf[fdf["FoodRating"] >= min_food]
if only_elec_inc:
    fdf = fdf[fdf["Electricity"] == "Included in rent"]
if only_4w_parking:
    fdf = fdf[fdf["ParkingCategory"] == "2 & 4 Wheeler"]
if hide_warnings:
    fdf = fdf[fdf["Warnings"].apply(len) == 0]

if search_query.strip():
    q = search_query.strip()
    mask = (
        fdf["Name"].str.contains(q, case=False, na=False)
        | fdf["Location"].str.contains(q, case=False, na=False)
        | fdf["Comments"].str.contains(q, case=False, na=False)
        | fdf["HighlightsStr"].str.contains(q, case=False, na=False)
    )
    fdf = fdf[mask]


# ─────────────────────────────────────────────────────────────────────────────
#  MASTHEAD BANNER
# ─────────────────────────────────────────────────────────────────────────────
render_html(
    f"""
    <div class="masthead">
        <div class="masthead-top">
            <div>
                <div class="masthead-title">Hyderabad PG Directory & Rent Intelligence</div>
                <p class="masthead-sub">
                    Crowdsourced by the <b>r/hyderabad</b> community — {len(df_all)} verified resident reviews across
                    {df_all['Location'].nunique()} neighborhoods with direct owner contacts, food ratings, and zero broker fees.
                </p>
            </div>
            <div class="masthead-actions">
                <a class="btn-primary" href="{FORM_URL}" target="_blank" rel="noopener">+ Submit a PG Review</a>
                <a class="btn-outline" href="{SHEET_EDIT_URL}" target="_blank" rel="noopener">Raw Google Sheet ↗</a>
            </div>
        </div>
    </div>
    """
)

# ─────────────────────────────────────────────────────────────────────────────
#  TOP-LEVEL NAVIGATION TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_directory, tab_calculator, tab_compare, tab_map, tab_about = st.tabs(
    [
        f"Directory & Reviews ({len(fdf)})",
        "Fair Rent Calculator & Market Insights",
        "Compare Shortlist",
        "Commute & Neighborhood Guide",
        "About & Recent Submissions",
    ]
)


# ═════════════════════════════════════════════════════════════════════════════
#  TAB 1: DIRECTORY & REVIEWS
# ═════════════════════════════════════════════════════════════════════════════
with tab_directory:
    if fdf.empty:
        st.info("No PGs match your current filter settings. Try increasing the budget slider or clearing sidebar filters.")
    else:
        med_rent = int(fdf["Cost"].median())
        avg_rent = int(fdf["Cost"].mean())
        rated_sub = fdf[fdf["Rating"] > 0]
        avg_rat = rated_sub["Rating"].mean() if not rated_sub.empty else 0.0
        avg_fd = fdf[fdf["FoodRating"] > 0]["FoodRating"].mean() if not fdf[fdf["FoodRating"] > 0].empty else 0.0
        elec_inc_pct = int(round((fdf["Electricity"] == "Included in rent").mean() * 100))
        with_phone_cnt = int((fdf["PhoneDigits"] != "").sum())

        render_html(
            f"""
            <div class="kpi-grid">
                <div class="kpi-box">
                    <div class="kpi-label">Matching Listings</div>
                    <div class="kpi-val">{len(fdf)} <span style="font-size:0.85rem;font-weight:500;opacity:0.65;">/ {len(df_all)} total</span></div>
                    <div class="kpi-sub">{with_phone_cnt} with direct owner phone</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-label">Median Monthly Rent</div>
                    <div class="kpi-val">₹{med_rent:,}</div>
                    <div class="kpi-sub">Average: ₹{avg_rent:,}/mo</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-label">Resident Rating</div>
                    <div class="kpi-val">{avg_rat:.2f} ★</div>
                    <div class="kpi-sub">Food Quality Avg: {avg_fd:.1f} / 5</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-label">All-Inclusive Rent</div>
                    <div class="kpi-val">{elec_inc_pct}%</div>
                    <div class="kpi-sub">Include electricity in base rent</div>
                </div>
            </div>
            """
        )

        # Controls Bar: Sort, View Switcher, Export
        ctrl1, ctrl2, ctrl3 = st.columns([1.8, 1.4, 1.0])
        with ctrl1:
            sort_options = [
                "Recommended (Best Reviewed & Fair Value)",
                "Highest Resident Rating",
                "Lowest Monthly Rent",
                "Highest Food Quality",
                "Newest Reviews First",
            ]
            if OFFICE_HUBS[sel_hub] is not None:
                sort_options.insert(0, "Closest to Selected Office Hub")
            sort_choice = st.selectbox("Sort Listings By", sort_options, label_visibility="collapsed")
        with ctrl2:
            view_mode = st.radio(
                "Display Mode",
                ["Review Cards", "Compact Table"],
                horizontal=True,
                label_visibility="collapsed",
            )
        with ctrl3:
            export_cols = [
                "Name",
                "Location",
                "PGType",
                "Sharing",
                "Cost",
                "Electricity",
                "Rating",
                "FoodRating",
                "RoomSpace",
                "ParkingCategory",
                "NearestMetro",
                "MetroDistKm",
                "Phone",
                "HighlightsStr",
                "WarningsStr",
                "Comments",
            ]
            st.download_button(
                "Export CSV",
                data=fdf[export_cols].to_csv(index=False).encode("utf-8"),
                file_name="hyderabad_pg_directory.csv",
                mime="text/csv",
                use_container_width=True,
            )

        # Apply Sorting
        if sort_choice == "Closest to Selected Office Hub":
            fdf = fdf.sort_values(["OfficeDistKm", "RecScore"], ascending=[True, False])
        elif sort_choice == "Recommended (Best Reviewed & Fair Value)":
            fdf = fdf.sort_values(["RecScore", "CompositeRating", "Cost"], ascending=[False, False, True])
        elif sort_choice == "Highest Resident Rating":
            fdf = fdf.sort_values(["Rating", "FoodRating", "Cost"], ascending=[False, False, True])
        elif sort_choice == "Lowest Monthly Rent":
            fdf = fdf.sort_values(["Cost", "Rating"], ascending=[True, False])
        elif sort_choice == "Highest Food Quality":
            fdf = fdf.sort_values(["FoodRating", "Rating", "Cost"], ascending=[False, False, True])
        elif sort_choice == "Newest Reviews First":
            fdf = fdf.sort_values("SubmittedAt", ascending=False, na_position="last")

        fdf = fdf.reset_index(drop=True)

        # ── VIEW A: STUDIO-GRADE PROPERTY REVIEW CARDS ──
        if view_mode == "Review Cards":
            page_size = 10
            total_pages = max(1, math.ceil(len(fdf) / page_size))
            pcol1, pcol2, _ = st.columns([1.1, 2.2, 1.5])
            with pcol1:
                curr_page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
            with pcol2:
                st.write("")
                start_i = (curr_page - 1) * page_size + 1
                end_i = min(curr_page * page_size, len(fdf))
                st.caption(f"Showing **{start_i}–{end_i}** of **{len(fdf)}** matching PGs")

            page_df = fdf.iloc[(curr_page - 1) * page_size : curr_page * page_size]

            for _, row in page_df.iterrows():
                name_esc = html.escape(str(row["Name"]))
                loc_esc = html.escape(str(row["Location"]))
                sharing_esc = html.escape(str(row["Sharing"]))
                pg_type = str(row["PGType"])

                if pg_type == "Men's PG":
                    type_badge = "<span class='badge badge-male'>Men's PG</span>"
                elif pg_type == "Women's PG":
                    type_badge = "<span class='badge badge-female'>Women's PG</span>"
                else:
                    type_badge = "<span class='badge badge-colive'>Co-Living</span>"

                commute_pill = (
                    f"<span class='badge badge-neutral'>~{row['OfficeDistKm']} km to Office</span>"
                    if pd.notna(row.get("OfficeDistKm"))
                    else ""
                )

                elec_is_inc = row["Electricity"] == "Included in rent"
                elec_html = (
                    "<div class='prop-elec elec-inc'>✓ Electricity included</div>"
                    if elec_is_inc
                    else f"<div class='prop-elec elec-sep'>+ Separate electricity (~₹{int(row['EstTotalCost']):,}/mo est.)</div>"
                )

                tags_parts = []
                for h_tag in row["Highlights"]:
                    tags_parts.append(f"<span class='tag-pos'>✓ {html.escape(h_tag)}</span>")
                for w_tag in row["Warnings"]:
                    tags_parts.append(f"<span class='tag-warn'>! {html.escape(w_tag)}</span>")
                tags_row_html = f"<div class='tag-row'>{''.join(tags_parts)}</div>" if tags_parts else ""

                raw_comment = str(row["Comments"]).strip()
                if raw_comment:
                    formatted_comment = "<br>".join(
                        html.escape(line) for line in raw_comment.splitlines()
                    )
                    comment_html = f"<div class='review-box'>{formatted_comment}</div>"
                else:
                    comment_html = "<div style='font-size:0.83rem;opacity:0.6;margin:0.45rem 0;'>No written commentary submitted — structured ratings only.</div>"

                date_str = row["SubmittedAt"].strftime("%b %d, %Y") if pd.notna(row["SubmittedAt"]) else "Community Verified"
                contrib_esc = html.escape(str(row["Contributor"]))

                action_links = [
                    f"<a class='card-link' href='{row['MapsURL']}' target='_blank' rel='noopener'>Google Maps ↗</a>"
                ]
                if row["PhoneDigits"]:
                    action_links.append(
                        f"<a class='card-link card-link-wa' href='https://wa.me/91{row['PhoneDigits']}' target='_blank' rel='noopener'>WhatsApp Owner ↗</a>"
                    )
                    action_links.append(
                        f"<a class='card-link' href='tel:+91{row['PhoneDigits']}'>Call {html.escape(row['Phone'])}</a>"
                    )
                else:
                    action_links.append("<span style='font-size:0.76rem;opacity:0.55;padding:0.25rem 0.4rem;'>No phone listed</span>")

                render_html(
                    f"""
                    <div class="prop-card">
                        <div class="prop-header">
                            <div>
                                <div class="prop-name">{name_esc}</div>
                                <div class="prop-meta">
                                    <span class="badge badge-area">{loc_esc}</span>
                                    {type_badge}
                                    <span class="badge badge-neutral">{sharing_esc}</span>
                                    {commute_pill}
                                    <span>• ~{row['MetroDistKm']} km to <b>{html.escape(row['NearestMetro'])} Metro</b></span>
                                </div>
                            </div>
                            <div class="prop-price-block">
                                <div class="prop-price">₹{int(row['Cost']):,}<span class="prop-price-unit">/mo</span></div>
                                {elec_html}
                            </div>
                        </div>
                        <div class="specs-strip">
                            <div class="spec-item"><span class="spec-label">Overall Rating:</span> <span class="spec-val">{row['Rating']:.1f} / 5 ★</span></div>
                            <div class="spec-item"><span class="spec-label">Food Quality:</span> <span class="spec-val">{row['FoodRating']:.1f} / 5</span></div>
                            <div class="spec-item"><span class="spec-label">Room Space:</span> <span class="spec-val">{html.escape(row['RoomSpace'])}</span></div>
                            <div class="spec-item"><span class="spec-label">Parking:</span> <span class="spec-val">{html.escape(row['ParkingCategory'])}</span></div>
                            <div class="spec-item"><span class="spec-label">Value Score:</span> <span class="spec-val">{row['ValueScore']:.1f} / 10</span></div>
                        </div>
                        {tags_row_html}
                        {comment_html}
                        <div class="prop-footer">
                            <div class="prop-credit">Reviewed by <b>{contrib_esc}</b> • {date_str}</div>
                            <div class="prop-links">{''.join(action_links)}</div>
                        </div>
                    </div>
                    """
                )

        # ── VIEW B: COMPACT DATA TABLE ──
        else:
            table_cols = [
                "Name",
                "Location",
                "PGType",
                "Sharing",
                "Cost",
                "Electricity",
                "Rating",
                "FoodRating",
                "ValueScore",
                "RoomSpace",
                "ParkingCategory",
                "NearestMetro",
                "Phone",
                "MapsURL",
                "Comments",
            ]
            if OFFICE_HUBS[sel_hub] is not None:
                table_cols.insert(2, "OfficeDistKm")

            st.dataframe(
                fdf[table_cols],
                hide_index=True,
                use_container_width=True,
                height=560,
                column_config={
                    "Name": st.column_config.TextColumn("Property Name", width="medium"),
                    "Location": st.column_config.TextColumn("Locality", width="small"),
                    "OfficeDistKm": st.column_config.NumberColumn("Office Dist", format="%.1f km"),
                    "PGType": st.column_config.TextColumn("Type", width="small"),
                    "Sharing": st.column_config.TextColumn("Sharing", width="small"),
                    "Cost": st.column_config.NumberColumn("Rent / Mo", format="₹%d"),
                    "Electricity": st.column_config.TextColumn("Electricity", width="small"),
                    "Rating": st.column_config.NumberColumn("Rating", format="%.1f ★"),
                    "FoodRating": st.column_config.NumberColumn("Food", format="%.1f ★"),
                    "ValueScore": st.column_config.ProgressColumn(
                        "Value Score",
                        format="%.1f",
                        min_value=0,
                        max_value=float(max(12.0, df_all["ValueScore"].max())),
                    ),
                    "RoomSpace": st.column_config.TextColumn("Space", width="small"),
                    "ParkingCategory": st.column_config.TextColumn("Parking", width="small"),
                    "NearestMetro": st.column_config.TextColumn("Nearest Metro", width="small"),
                    "Phone": st.column_config.TextColumn("Owner Phone", width="small"),
                    "MapsURL": st.column_config.LinkColumn("Maps", display_text="Open Map ↗", width="small"),
                    "Comments": st.column_config.TextColumn("Resident Review", width="large"),
                },
            )


# ═════════════════════════════════════════════════════════════════════════════
#  TAB 2: FAIR RENT CALCULATOR & MARKET INSIGHTS
# ═════════════════════════════════════════════════════════════════════════════
with tab_calculator:
    st.subheader('Fair Rent Benchmark Calculator — "Am I Overpaying?"')
    st.caption(
        "Check whether a quoted rent is fair compared to actual resident-reported rents in the same locality and room configuration."
    )

    bcol1, bcol2, bcol3, bcol4 = st.columns([1.3, 1.1, 1.1, 1.1])
    with bcol1:
        top_areas_for_calc = df_all["Location"].value_counts().index.tolist()
        calc_loc = st.selectbox("Select Locality", ["All Hyderabad"] + top_areas_for_calc, index=1 if len(top_areas_for_calc) > 0 else 0)
    with bcol2:
        calc_sharing = st.selectbox("Select Room Sharing", ["Two Sharing", "Triple Sharing", "Four Sharing", "Single"], index=0)
    with bcol3:
        calc_type = st.selectbox("Accommodation Type", ["Any", "Men's PG", "Women's PG", "Co-Living"], index=0)
    with bcol4:
        quoted_rent = st.number_input("Quoted Monthly Rent (₹)", min_value=3000, max_value=50000, value=12000, step=500)

    bench_df = df_all[df_all["Sharing"] == calc_sharing].copy()
    if calc_loc != "All Hyderabad":
        bench_df = bench_df[bench_df["Location"] == calc_loc]
    if calc_type != "Any":
        bench_df = bench_df[bench_df["PGType"] == calc_type]

    sample_note = f"{len(bench_df)} exact matches in {calc_loc}"
    if len(bench_df) < 3:
        bench_df = df_all[df_all["Sharing"] == calc_sharing].copy()
        sample_note = f"Citywide benchmark for {calc_sharing} ({len(bench_df)} listings; limited local sample in {calc_loc})"

    if not bench_df.empty:
        p25 = int(np.percentile(bench_df["Cost"], 25))
        p50 = int(np.percentile(bench_df["Cost"], 50))
        p75 = int(np.percentile(bench_df["Cost"], 75))
        diff = quoted_rent - p50

        if quoted_rent <= p25:
            verdict = "Great Deal (Below 25th Percentile)"
            verdict_color = "#10b981"
        elif quoted_rent <= p75:
            verdict = "Fair Market Rate (Within Typical Range)"
            verdict_color = "#3b82f6"
        else:
            verdict = f"Above Market Rate (+₹{diff:,} over median)"
            verdict_color = "#ef4444"

        render_html(
            f"""
            <div class="kpi-grid" style="margin-top:0.5rem;">
                <div class="kpi-box">
                    <div class="kpi-label">Price Verdict</div>
                    <div class="kpi-val" style="color:{verdict_color};font-size:1.1rem;">{verdict}</div>
                    <div class="kpi-sub">{sample_note}</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-label">Budget Tier (25th Pct)</div>
                    <div class="kpi-val">₹{p25:,}/mo</div>
                    <div class="kpi-sub">Lower end of market</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-label">Market Median</div>
                    <div class="kpi-val">₹{p50:,}/mo</div>
                    <div class="kpi-sub">Typical rent paid by residents</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-label">Premium Tier (75th Pct)</div>
                    <div class="kpi-val">₹{p75:,}/mo</div>
                    <div class="kpi-sub">Co-living / AC / luxury stays</div>
                </div>
            </div>
            """
        )

    st.divider()
    st.subheader("Market Analytics & Pricing Structure")

    c_chart1, c_chart2 = st.columns(2)
    with c_chart1:
        st.markdown("**Median Rent by Locality & Room Sharing (Top Hubs)**")
        top8_locs = df_all["Location"].value_counts().head(8).index.tolist()
        loc_share_df = (
            df_all[df_all["Location"].isin(top8_locs) & df_all["Sharing"].isin(["Single", "Two Sharing", "Triple Sharing", "Four Sharing"])]
            .groupby(["Location", "Sharing"], as_index=False)["Cost"]
            .median()
        )
        fig_bar = px.bar(
            loc_share_df,
            x="Location",
            y="Cost",
            color="Sharing",
            barmode="group",
            text_auto=".0f",
            category_orders={"Sharing": ["Single", "Two Sharing", "Triple Sharing", "Four Sharing"]},
            color_discrete_sequence=["#1e40af", "#3b82f6", "#10b981", "#f59e0b"],
            labels={"Cost": "Median Monthly Rent (₹)", "Location": "Locality"},
        )
        fig_bar.update_layout(
            height=390,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, title=None),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c_chart2:
        st.markdown("**Value Frontier: Monthly Rent vs. Resident Rating**")
        rated_all = df_all[df_all["Rating"] > 0].copy()
        rated_all["BubbleSize"] = rated_all["FoodRating"].clip(lower=1.0) * 3.5
        fig_scat = px.scatter(
            rated_all,
            x="Cost",
            y="CompositeRating",
            color="PGType",
            size="BubbleSize",
            hover_name="Name",
            hover_data=["Location", "Sharing", "Rating", "FoodRating", "Electricity"],
            color_discrete_map={
                "Co-Living": "#8b5cf6",
                "Men's PG": "#0ea5e9",
                "Women's PG": "#ec4899",
            },
            labels={"Cost": "Monthly Rent (₹)", "CompositeRating": "Composite Rating (Overall + Food)", "PGType": "Type"},
        )
        fig_scat.update_layout(
            height=390,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, title=None),
        )
        st.plotly_chart(fig_scat, use_container_width=True)

    c_chart3, c_chart4 = st.columns(2)
    with c_chart3:
        st.markdown("**Rent Distribution by Room Space Perception**")
        fig_box = px.box(
            df_all,
            x="RoomSpace",
            y="Cost",
            color="RoomSpace",
            points="all",
            hover_name="Name",
            hover_data=["Location", "Sharing"],
            category_orders={"RoomSpace": ["Spacious", "Average", "Cramped"]},
            color_discrete_sequence=["#10b981", "#3b82f6", "#ef4444"],
            labels={"RoomSpace": "Room Space Reported by Residents", "Cost": "Monthly Rent (₹)"},
        )
        fig_box.update_layout(
            height=360,
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_box, use_container_width=True)

    with c_chart4:
        st.markdown("**Top 10 Best Recommended Stays (Rating ≥ 4.0 & Verified)**")
        best_val_df = (
            df_all[(df_all["Rating"] >= 4.0) & (df_all["Warnings"].apply(len) == 0)]
            .sort_values(["RecScore", "CompositeRating"], ascending=[False, False])
            .head(10)
        )
        st.dataframe(
            best_val_df[["Name", "Location", "PGType", "Sharing", "Cost", "Rating", "FoodRating", "Phone"]],
            hide_index=True,
            use_container_width=True,
            height=350,
            column_config={
                "Name": st.column_config.TextColumn("PG Name"),
                "Location": st.column_config.TextColumn("Area"),
                "PGType": st.column_config.TextColumn("Type"),
                "Sharing": st.column_config.TextColumn("Sharing"),
                "Cost": st.column_config.NumberColumn("Rent", format="₹%d"),
                "Rating": st.column_config.NumberColumn("Rating", format="%.1f ★"),
                "FoodRating": st.column_config.NumberColumn("Food", format="%.1f ★"),
            },
        )


# ═════════════════════════════════════════════════════════════════════════════
#  TAB 3: COMPARE SHORTLIST
# ═════════════════════════════════════════════════════════════════════════════
with tab_compare:
    st.subheader("Side-by-Side PG Comparison")
    st.caption("Select 2 to 4 properties to compare rent, estimated total cost with electricity, food quality, and resident reviews.")

    source_pool = fdf if len(fdf) >= 2 else df_all
    source_pool = source_pool.copy()
    source_pool["OptionLabel"] = source_pool.apply(
        lambda r: f"{r['Name']} — {r['Location']} ({r['Sharing']}, ₹{int(r['Cost']):,}/mo)",
        axis=1,
    )
    default_picks = source_pool["OptionLabel"].head(min(3, len(source_pool))).tolist()
    chosen_labels = st.multiselect(
        "Choose properties to compare (max 4)",
        options=source_pool["OptionLabel"].tolist(),
        default=default_picks,
        max_selections=4,
    )

    if len(chosen_labels) < 2:
        st.info("Select at least 2 properties above to generate a side-by-side comparison.")
    else:
        comp_rows = source_pool[source_pool["OptionLabel"].isin(chosen_labels)].copy()

        matrix_records = []
        spec_fields = [
            ("Locality", "Location"),
            ("Accommodation Type", "PGType"),
            ("Room Sharing", "Sharing"),
            ("Base Monthly Rent", lambda r: f"₹{int(r['Cost']):,}/mo"),
            ("Electricity Billing", "Electricity"),
            ("Est. All-In Monthly Cost", lambda r: f"₹{int(r['EstTotalCost']):,}/mo"),
            ("Overall Resident Rating", lambda r: f"{r['Rating']:.1f} / 5.0 ★"),
            ("Food Quality Rating", lambda r: f"{r['FoodRating']:.1f} / 5.0 ★"),
            ("Value Score (Tier-Adjusted)", lambda r: f"{r['ValueScore']:.1f} / 10"),
            ("Room Space", "RoomSpace"),
            ("Parking", "ParkingCategory"),
            ("Nearest Metro Station", lambda r: f"{r['NearestMetro']} (~{r['MetroDistKm']} km)"),
            ("Highlights", "HighlightsStr"),
            ("Reported Warnings", "WarningsStr"),
            ("Owner Phone", "Phone"),
        ]
        for label_name, getter in spec_fields:
            row_dict = {"Specification": label_name}
            for idx_num, (_, r) in enumerate(comp_rows.iterrows(), start=1):
                col_key = f"{idx_num}. {r['Name'][:26]}"
                row_dict[col_key] = getter(r) if callable(getter) else str(r.get(getter, "—"))
            matrix_records.append(row_dict)

        st.dataframe(pd.DataFrame(matrix_records), hide_index=True, use_container_width=True)

        st.markdown("#### Full Resident Reviews & Direct Links")
        ui_cols = st.columns(len(comp_rows))
        for col_ui, (_, crow) in zip(ui_cols, comp_rows.iterrows()):
            with col_ui:
                st.markdown(f"**{crow['Name']}**")
                st.caption(f"{crow['Location']} • {crow['Sharing']} • ₹{int(crow['Cost']):,}/mo")
                st.info(crow["Comments"] if crow["Comments"] else "No written review comment provided.")
                st.link_button("Open in Google Maps ↗", crow["MapsURL"], use_container_width=True)
                if crow["PhoneDigits"]:
                    st.link_button(
                        f"WhatsApp {crow['Phone']}",
                        f"https://wa.me/91{crow['PhoneDigits']}",
                        use_container_width=True,
                    )


# ═════════════════════════════════════════════════════════════════════════════
#  TAB 4: COMMUTE & NEIGHBORHOOD GUIDE
# ═════════════════════════════════════════════════════════════════════════════
with tab_map:
    st.subheader("Hyderabad Locality Guide & Transit Map")
    st.caption(
        "Compare neighborhoods by median rent, resident satisfaction, and distance to major IT corridors and Metro stations."
    )

    mctrl1, mctrl2 = st.columns([1.8, 1.2])
    with mctrl1:
        hub_choices = [k for k in OFFICE_HUBS.keys() if OFFICE_HUBS[k] is not None]
        default_hub_idx = 0
        if sel_hub in hub_choices:
            default_hub_idx = hub_choices.index(sel_hub)
        guide_hub = st.selectbox("Reference Office Hub for Commute Distance", hub_choices, index=default_hub_idx)
    with mctrl2:
        map_color_by = st.selectbox("Color Map Clusters By", ["Median Monthly Rent (₹)", "Average Resident Rating"])

    g_lat, g_lon = OFFICE_HUBS[guide_hub]

    area_summary = (
        df_all.groupby("Location", as_index=False)
        .agg(
            Listings=("Name", "count"),
            MedianRent=("Cost", "median"),
            MinRent=("Cost", "min"),
            MaxRent=("Cost", "max"),
            AvgRating=("Rating", "mean"),
            AvgFood=("FoodRating", "mean"),
            AreaLat=("AreaLat", "first"),
            AreaLon=("AreaLon", "first"),
            NearestMetro=("NearestMetro", "first"),
            MetroLine=("MetroLine", "first"),
            MetroDistKm=("MetroDistKm", "first"),
        )
    )
    area_summary["MedianRent"] = area_summary["MedianRent"].round(0).astype(int)
    area_summary["AvgRating"] = area_summary["AvgRating"].round(2)
    area_summary["AvgFood"] = area_summary["AvgFood"].round(2)
    area_summary["OfficeDistKm"] = area_summary.apply(
        lambda r: round(haversine_km(r["AreaLat"], r["AreaLon"], g_lat, g_lon), 1),
        axis=1,
    )

    top_pg_per_loc = (
        df_all.sort_values(["RecScore", "CompositeRating"], ascending=[False, False])
        .groupby("Location", as_index=False)
        .first()[["Location", "Name"]]
        .rename(columns={"Name": "TopRatedPG"})
    )
    area_summary = area_summary.merge(top_pg_per_loc, on="Location", how="left")
    area_summary = area_summary.sort_values(["OfficeDistKm", "Listings"], ascending=[True, False]).reset_index(drop=True)

    color_field = "MedianRent" if map_color_by == "Median Monthly Rent (₹)" else "AvgRating"
    use_maplibre = hasattr(go, "Scattermap")
    trace_cls = go.Scattermap if use_maplibre else go.Scattermapbox

    try:
        map_fn = px.scatter_map if hasattr(px, "scatter_map") else px.scatter_mapbox
        style_kw = {"map_style": "carto-positron"} if hasattr(px, "scatter_map") else {"mapbox_style": "carto-positron"}
        fig_map = map_fn(
            area_summary,
            lat="AreaLat",
            lon="AreaLon",
            size="Listings",
            size_max=28,
            color=color_field,
            hover_name="Location",
            hover_data={
                "Listings": True,
                "MedianRent": ":₹,.0f",
                "AvgRating": ":.2f",
                "AvgFood": ":.2f",
                "OfficeDistKm": True,
                "NearestMetro": True,
                "TopRatedPG": True,
                "AreaLat": False,
                "AreaLon": False,
            },
            zoom=11.0,
            center={"lat": g_lat, "lon": g_lon},
            height=500,
            color_continuous_scale="Plasma" if color_field == "MedianRent" else "Viridis",
            **style_kw,
        )
    except Exception:
        fig_map = go.Figure(
            trace_cls(
                lat=area_summary["AreaLat"],
                lon=area_summary["AreaLon"],
                mode="markers",
                name="Localities",
                marker=dict(
                    size=np.clip(area_summary["Listings"] * 2 + 10, 10, 28),
                    color=area_summary[color_field],
                    colorscale="Plasma" if color_field == "MedianRent" else "Viridis",
                    showscale=True,
                ),
                text=area_summary.apply(
                    lambda r: f"<b>{r['Location']}</b> ({r['Listings']} PGs)<br>Median Rent: ₹{r['MedianRent']:,}/mo | Avg Rating: {r['AvgRating']}★<br>Dist to Office: {r['OfficeDistKm']} km",
                    axis=1,
                ),
                hoverinfo="text",
            )
        )
        layout_key = "map" if use_maplibre else "mapbox"
        fig_map.update_layout(
            **{layout_key: dict(style="carto-positron", center=dict(lat=g_lat, lon=g_lon), zoom=11.0)},
            height=500,
        )

    metro_df = pd.DataFrame(METRO_STATIONS)
    line_colors = {"Blue Line": "#2563eb", "Red Line": "#dc2626", "Green Line": "#16a34a"}
    for line_name, ldf in metro_df.groupby("line", sort=False):
        fig_map.add_trace(
            trace_cls(
                lat=ldf["lat"],
                lon=ldf["lon"],
                mode="lines+markers",
                name=f"Metro {line_name}",
                line=dict(width=2.5, color=line_colors.get(line_name, "#2563eb")),
                marker=dict(size=7, color=line_colors.get(line_name, "#2563eb")),
                text=ldf["station"] + " Metro Station (" + ldf["line"] + ")",
                hoverinfo="text",
            )
        )

    fig_map.add_trace(
        trace_cls(
            lat=[g_lat],
            lon=[g_lon],
            mode="markers+text",
            name=f"Office: {guide_hub.split('(')[0].strip()}",
            marker=dict(size=16, color="#0f172a"),
            text=[guide_hub.split("(")[0].strip()],
            textposition="top right",
            hoverinfo="text",
        )
    )

    fig_map.update_layout(margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", yanchor="bottom", y=1.01))
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown(f"#### Neighborhood Comparison Table (Sorted by Proximity to {guide_hub.split('(')[0].strip()})")
    st.dataframe(
        area_summary[
            [
                "Location",
                "OfficeDistKm",
                "Listings",
                "MedianRent",
                "AvgRating",
                "AvgFood",
                "NearestMetro",
                "MetroDistKm",
                "TopRatedPG",
            ]
        ],
        hide_index=True,
        use_container_width=True,
        height=440,
        column_config={
            "Location": st.column_config.TextColumn("Neighborhood"),
            "OfficeDistKm": st.column_config.NumberColumn("Dist to Office", format="%.1f km"),
            "Listings": st.column_config.NumberColumn("Verified PGs", format="%d"),
            "MedianRent": st.column_config.NumberColumn("Median Rent", format="₹%d/mo"),
            "AvgRating": st.column_config.NumberColumn("Avg Rating", format="%.2f ★"),
            "AvgFood": st.column_config.NumberColumn("Avg Food", format="%.2f ★"),
            "NearestMetro": st.column_config.TextColumn("Nearest Metro"),
            "MetroDistKm": st.column_config.NumberColumn("Metro Dist", format="%.1f km"),
            "TopRatedPG": st.column_config.TextColumn("Top Rated PG in Area"),
        },
    )


# ═════════════════════════════════════════════════════════════════════════════
#  TAB 5: ABOUT & RECENT SUBMISSIONS
# ═════════════════════════════════════════════════════════════════════════════
with tab_about:
    acol1, acol2 = st.columns([1.4, 1.0])
    with acol1:
        st.subheader("About the r/hyderabad PG Directory")
        st.markdown(
            """
            Finding decent accommodation in Hyderabad often means dealing with inflated broker commissions,
            misleading room photos, unreturned security deposits, and surprise electricity bills.

            To make PG hunting transparent, members of the **r/hyderabad** Reddit community created an open,
            crowdsourced ledger of PG and Co-Living reviews:

            * **Initial Community Database:** [Let's build the ultimate Hyderabad PG database!](https://www.reddit.com/r/hyderabad/comments/1mzjwfj/lets_build_the_ultimate_hyderabad_pg_database/)
            * **Live Dashboard Launch:** [I built a live dashboard to find PGs in Hyderabad](https://www.reddit.com/r/hyderabad/comments/1ppxvnz/i_built_a_live_dashboard_to_find_pgs_in_hyderabad/)

            Every entry comes directly from a current or former resident—no sponsored placements and no middlemen.
            """
        )

        st.markdown("#### Recent Resident Submissions")
        recent_df = df_all.sort_values("SubmittedAt", ascending=False, na_position="last").head(10)
        st.dataframe(
            recent_df[["Name", "Location", "PGType", "Sharing", "Cost", "Rating", "FoodRating", "Contributor"]],
            hide_index=True,
            use_container_width=True,
            column_config={
                "Name": st.column_config.TextColumn("Property Name"),
                "Location": st.column_config.TextColumn("Locality"),
                "PGType": st.column_config.TextColumn("Type"),
                "Sharing": st.column_config.TextColumn("Sharing"),
                "Cost": st.column_config.NumberColumn("Rent", format="₹%d"),
                "Rating": st.column_config.NumberColumn("Rating", format="%.1f ★"),
                "FoodRating": st.column_config.NumberColumn("Food", format="%.1f ★"),
                "Contributor": st.column_config.TextColumn("Reviewer"),
            },
        )

    with acol2:
        st.subheader("Contribute Your Review")
        st.write(
            "Lived in a Hyderabad PG or Co-Living space? Share your honest rent, food quality score, and owner contact "
            "to help newcomers avoid bad stays. Submissions sync automatically with this live directory."
        )
        st.link_button("Submit a PG Review (Google Form) ↗", FORM_URL, use_container_width=True)
        st.link_button("Inspect Raw Google Sheet ↗", SHEET_EDIT_URL, use_container_width=True)

        st.divider()
        st.markdown("#### Methodology & Scoring")
        st.markdown(
            """
            * **Composite Rating:** Combines Overall Resident Rating ($70\\%$) and Food Quality Rating ($30\\%$).
            * **Estimated All-In Cost:** Adds an ₹800/mo buffer when electricity is billed separately so you can compare all-inclusive vs. metered PGs fairly.
            * **Sharing-Adjusted Value Score:** Compares each PG's all-in cost against the median rent for the **same room-sharing tier** (Single vs. Single, 2-Sharing vs. 2-Sharing), so 2-sharing and single rooms in prime IT hubs are evaluated fairly alongside 4-sharing rooms.
            """
        )
