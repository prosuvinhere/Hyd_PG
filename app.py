import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="PG Hyderabad Directory",
    layout="wide"
)

# ─────────────────────────────────────────────
#  VIEW COUNTER LOGIC (FILE-BASED)
# ─────────────────────────────────────────────
COUNTER_FILE = "view_count.txt"

# Only increment if this specific user hasn't logged a view yet in this session
if "view_logged" not in st.session_state:
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "r") as f:
            try:
                count = int(f.read().strip())
            except ValueError:
                count = 2000
    else:
        count = 2000
        
    # Increment and save
    count += 1
    with open(COUNTER_FILE, "w") as f:
        f.write(str(count))
        
    st.session_state.view_logged = True

# Read the current count for display
if os.path.exists(COUNTER_FILE):
    with open(COUNTER_FILE, "r") as f:
        try:
            current_views = int(f.read().strip())
        except ValueError:
            current_views = 2000
else:
    current_views = 2000

# ─────────────────────────────────────────────
#  NAVIGATION
# ─────────────────────────────────────────────
page = st.sidebar.radio(
    "Navigation", 
    ["Search & Analytics", "Metro Map", "Add a PG & Info"]
)

# Display the counter at the bottom of the sidebar
st.sidebar.divider()
st.sidebar.metric("👁️ Total Views", f"{current_views:,}")


# ─────────────────────────────────────────────
#  DATA LOADING & CLEANING
# ─────────────────────────────────────────────
def clean_cost(x):
    if isinstance(x, str):
        s = x.replace("₹", "").replace(",", "").strip()
        if "-" in s:
            try: return (float(s.split("-")[0].strip()) + float(s.split("-")[1].strip())) / 2
            except: return 0
        try: return float(s)
        except: return 0
    return float(x) if x else 0

@st.cache_data(ttl=600)
def load_data():
    try:
        url = "https://docs.google.com/spreadsheets/d/1AW4EKm412u_UyYhf1swdhDsP5ikadr3XXeUTMrqvh4w/export?format=csv&gid=1856698473"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        df.rename(columns={
            "Name of PG/Hostel:": "Name", 
            "🌍 Location:": "Location",
            "🏡Type of Sharing:": "Sharing", 
            "💰 Monthly Cost (₹):": "Cost", 
            "Overall Rating:": "Rating",
            "Additional Comments:": "Comments", 
            "PG Owner Phone number": "Phone", 
            "Contributor Gender": "Gender",
        }, inplace=True)

        df["Cost"]     = df["Cost"].apply(clean_cost)
        df             = df[(df["Cost"] > 2000) & (df["Cost"] < 60000)]
        df["Rating"]   = pd.to_numeric(df["Rating"], errors="coerce").fillna(0)
        df["Location"] = df["Location"].fillna("Unknown").str.strip().str.title()
        df["Gender"]   = df["Gender"].fillna("Any").str.strip()
        df["Sharing"]  = df["Sharing"].fillna("Unknown").str.strip()
        df["Comments"] = df["Comments"].fillna("").str.strip()
        df["Name"]     = df["Name"].fillna("Unnamed PG").str.strip()
        df["Phone"]    = df["Phone"].fillna("").astype(str).str.strip()
        
        COORDS = {
            "Gachibowli": [17.4401, 78.3489], "Madhapur": [17.4483, 78.3915], "Kondapur": [17.4622, 78.3568],
            "Hitec City": [17.4435, 78.3772], "Jubilee Hills": [17.4325, 78.4070], "Banjara Hills": [17.4123, 78.4389],
            "Kukatpally": [17.4948, 78.3996], "Manikonda": [17.4018, 78.3846], "Nanakramguda": [17.4125, 78.3396],
            "Hafeezpet": [17.4856, 78.3526], "Ameerpet": [17.4375, 78.4483], "Unknown": [17.3850, 78.4867],
        }
        coords = df["Location"].map(lambda x: COORDS.get(x, COORDS["Unknown"]))
        df["lat"] = coords.map(lambda x: x[0]) + np.random.normal(0, 0.003, len(df))
        df["lon"] = coords.map(lambda x: x[1]) + np.random.normal(0, 0.003, len(df))
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()


# ══════════════════════════════════════════════
#  PAGE 1: COMBINED SEARCH & ANALYTICS
# ══════════════════════════════════════════════
if page == "Search & Analytics":
    df = load_data()
    
    st.title("PG Search & Analytics")
    st.write("Use the filters below to dynamically update both the list and the visualization charts.")
    
    if df.empty:
        st.stop()

    # ── GLOBAL FILTERS ──
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: 
        all_locs = sorted(df["Location"].unique().tolist())
        sel_loc = st.multiselect("Area(s)", all_locs, default=[])
    with col2: 
        sel_gender = st.selectbox("Gender", ["Any"] + sorted(df["Gender"].unique().tolist()))
    with col3: 
        sel_share = st.selectbox("Room Type", ["Any"] + sorted(df["Sharing"].dropna().unique().tolist()))
    with col4: 
        budget = st.slider("Max Budget", int(df["Cost"].min()), int(df["Cost"].max()), 25000, 500)
    with col5: 
        min_rat = st.slider("Min Rating", 0.0, 5.0, 0.0, 0.5)

    search = st.text_input("Search by PG name, area, or keywords in reviews...")

    # ── FILTER LOGIC ──
    fdf = df.copy()
    if sel_loc: 
        fdf = fdf[fdf["Location"].isin(sel_loc)]
    if sel_gender != "Any":    fdf = fdf[fdf["Gender"] == sel_gender]
    if sel_share != "Any":     fdf = fdf[fdf["Sharing"] == sel_share]
    fdf = fdf[(fdf["Cost"] <= budget) & (fdf["Rating"] >= min_rat)]

    if search.strip():
        q = search.strip()
        mask = (
            fdf["Name"].str.contains(q, case=False, na=False) |
            fdf["Location"].str.contains(q, case=False, na=False) |
            fdf["Comments"].str.contains(q, case=False, na=False)
        )
        fdf = fdf[mask]

    fdf = fdf.sort_values(["Rating", "Cost"], ascending=[False, True]).reset_index(drop=True)

    st.divider()

    if fdf.empty:
        st.info("No PGs match your current filter criteria. Try broadening your search.")
    else:
        # ── QUICK STATS ──
        k1, k2, k3, k4 = st.columns(4)
        rated_pgs = fdf[fdf["Rating"] > 0]
        avg_rent = fdf["Cost"].mean()
        avg_rating = rated_pgs["Rating"].mean() if not rated_pgs.empty else 0
        try: cheap_area = fdf.groupby("Location")["Cost"].mean().idxmin()
        except: cheap_area = "—"

        k1.metric("Matching PGs", f"{len(fdf)}")
        k2.metric("Average Monthly Rent", f"₹{int(avg_rent):,}")
        k3.metric("Average Rating", f"{avg_rating:.1f}")
        k4.metric("Most Affordable Area", cheap_area)
        
        st.write("")

        # ── TABS FOR DIRECTORY & ANALYTICS ──
        tab1, tab2 = st.tabs(["PG Directory", "Market Analytics"])

        # Tab 1: Data Table
        with tab1:
            cols = ["Name", "Location", "Sharing", "Gender", "Cost", "Rating", "Phone", "Comments"]
            st.dataframe(fdf[cols], hide_index=True, use_container_width=True)

        # Tab 2: Visual Graphs & Analytics
        with tab2:
            st.caption(f"Visualizing structural characteristics for {len(fdf)} active matching records.")
            
            r1c1, r1c2 = st.columns(2)
            with r1c1:
                st.subheader("Price Distribution Spectrum")
                fig0 = px.histogram(fdf, x="Cost", nbins=15)
                st.plotly_chart(fig0, use_container_width=True)
                
            with r1c2:
                st.subheader("Room Config Allocation")
                sharing_counts = fdf["Sharing"].value_counts().reset_index()
                sharing_counts.columns = ["Sharing Type", "Count"]
                fig2 = px.pie(sharing_counts, names="Sharing Type", values="Count", hole=0.4)
                st.plotly_chart(fig2, use_container_width=True)

            st.divider()
            r2c1, r2c2 = st.columns(2)
            with r2c1:
                st.subheader("Mean Budget Thresholds by Area")
                area_cost = fdf.groupby("Location")["Cost"].mean().reset_index().sort_values("Cost", ascending=True)
                fig1 = px.bar(area_cost, x="Cost", y="Location", orientation='h')
                st.plotly_chart(fig1, use_container_width=True)
                
            with r2c2:
                st.subheader("Rent Variation Profile")
                fig4 = px.box(fdf, x="Location", y="Cost", points="outliers")
                st.plotly_chart(fig4, use_container_width=True)

            st.divider()
            r3c1, r3c2 = st.columns(2)
            with r3c1:
                st.subheader("Price vs. Community Rating")
                if not rated_pgs.empty:
                    fig3 = px.scatter(rated_pgs, x="Cost", y="Rating", color="Location", hover_data=["Name", "Sharing"])
                    st.plotly_chart(fig3, use_container_width=True)
                else:
                    st.info("Insufficient feedback scores to plot a rating scatter index.")
                    
            with r3c2:
                st.subheader("Value-for-Money Indexes")
                if not rated_pgs.empty:
                    val_df = rated_pgs.copy()
                    val_df["ValueScore"] = (val_df["Rating"] ** 2) / val_df["Cost"]
                    top_value = val_df.sort_values("ValueScore", ascending=False).head(5)
                    st.dataframe(top_value[["Name", "Location", "Sharing", "Cost", "Rating"]], hide_index=True, use_container_width=True)
                else:
                    st.info("Value optimizing metrics require rated entries.")

# ══════════════════════════════════════════════
#  PAGE 2: METRO MAP
# ══════════════════════════════════════════════
elif page == "Metro Map":
    df = load_data()
    st.title("Hyderabad Metro Network")
    st.write("Reference the official transit coordinates below to pair your daily commute with a nearby residency area.")
    st.link_button("Launch Interactive Transit Link", "https://ltmetro.com/metro-network-map/")
    
    st.markdown("""
    ---
    ### Core Route Networks
    * **Red Line:** Miyapur ↔ LB Nagar *(via Ameerpet, MGBS, Dilsukhnagar)*
    * **Blue Line:** Raidurg ↔ Nagole *(via HITEC City, Jubilee Hills, Ameerpet, Secunderabad)*
    * **Green Line:** JBS Parade Ground ↔ MG Bus Station *(via Musheerabad, RTC X Roads)*
    """)
    
    st.write("### Geographic Listing Overlays")
    if not df.empty:
        st.map(df[["lat", "lon"]], use_container_width=True)

# ══════════════════════════════════════════════
#  PAGE 3: ADD A PG & LINKS
# ══════════════════════════════════════════════
elif page == "Add a PG & Info":
    st.title("The Story Behind the Directory")
    
    st.markdown("""
    Finding a reliable PG in Hyderabad can be a daunting task. Between exorbitant broker fees, misleading photos, and hidden monthly costs, the search process is often frustrating and opaque. 

    To solve this, the **r/hyderabad** community on Reddit came together to build a transparent, crowdsourced database of PG accommodations. 
    
    * **How it started:** It began with a simple idea in [this initial Reddit thread](https://www.reddit.com/r/hyderabad/comments/1mzjwfj/lets_build_the_ultimate_hyderabad_pg_database/), where users started dropping honest reviews, real prices, and direct owner contacts to bypass brokers.
    * **How it's going:** The static spreadsheet evolved into this live dashboard, as announced in [this follow-up launch post](https://www.reddit.com/r/hyderabad/comments/1ppxvnz/i_built_a_live_dashboard_to_find_pgs_in_hyderabad/).

    Today, this tool remains 100% community-driven. No brokers, no sponsored listings, no algorithms pushing expensive rooms—just real feedback from people who actually live there.
    """)

    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Submit your PG Review")
        st.write("Help the next person moving to the city. Submit your current or previous PG details below.")
        st.link_button("Launch Submission Portal", "https://docs.google.com/forms/d/e/1FAIpQLScXRf8vHeXwMeAbY_QLGDjGYemxD6BClUGffeOTTcra_9IBcQ/viewform")

    with col2:
        st.subheader("Raw Data & Links")
        st.write("Want to run your own analysis? The master Google Sheet containing all crowdsourced responses is public.")
        st.link_button("Open Shared Google Sheet", "https://docs.google.com/spreadsheets/d/1AW4EKm412u_UyYhf1swdhDsP5ikadr3XXeUTMrqvh4w/edit")
        
        st.write("")
        
        st.subheader("Join the Conversation")
        st.write("Want to suggest a feature, report a bug, or just say thanks? Drop a comment on the original Reddit threads:")
        st.markdown("""
        * [Part 1: Let's build the ultimate Hyderabad PG database!](https://www.reddit.com/r/hyderabad/comments/1mzjwfj/lets_build_the_ultimate_hyderabad_pg_database/)
        * [Part 2: I built a live dashboard to find PGs in Hyderabad](https://www.reddit.com/r/hyderabad/comments/1ppxvnz/i_built_a_live_dashboard_to_find_pgs_in_hyderabad/)
        """)
