import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="PG Hyderabad Directory",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal CSS to hide default header/footer for a cleaner look
st.markdown("""
<style>
#MainMenu, header, footer {visibility: hidden;}
.block-container {padding-top: 2rem !important; padding-bottom: 2rem !important;}
</style>
""", unsafe_allow_html=True)

# Custom color constant for consistent visualization theming
CHART_THEME = ["#1F77B4", "#FF7F0E", "#2CA02C", "#D62728", "#9467BD", "#8C564B", "#E377C2", "#7F7F7F"]

# ─────────────────────────────────────────────
#  NAVIGATION
# ─────────────────────────────────────────────
page = st.sidebar.radio(
    "Navigation", 
    ["📊 Search & Analytics", "🚇 Metro Map", "➕ Add a PG & Info"]
)

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
if page == "📊 Search & Analytics":
    df = load_data()
    
    st.title("📊 PG Search & Analytics")
    st.write("Use the filters below to dynamically update both the list and all structural visualization charts simultaneously.")
    
    if df.empty:
        st.stop()

    # ── GLOBAL FILTERS ──
    c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 3, 2])
    with c1: 
        all_locs = sorted(df["Location"].unique().tolist())
        sel_loc = st.multiselect("📍 Area(s)", all_locs, default=[], placeholder="All Areas (Leave empty)")
    with c2: 
        sel_gender = st.selectbox("🚻 Gender", ["Any"] + sorted(df["Gender"].unique().tolist()))
    with c3: 
        sel_share = st.selectbox("🏠 Room Type", ["Any"] + sorted(df["Sharing"].dropna().unique().tolist()))
    with c4: 
        budget = st.slider("💰 Max Budget", int(df["Cost"].min()), int(df["Cost"].max()), 25000, 500, format="₹%d")
    with c5: 
        min_rat = st.slider("⭐ Min Rating", 0.0, 5.0, 0.0, 0.5)

    search = st.text_input("🔍 Search", placeholder="Search by PG name, area, or keywords in reviews...", label_visibility="collapsed")

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

    st.markdown("---")

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
        k3.metric("Average Rating", f"{avg_rating:.1f} ⭐")
        k4.metric("Most Affordable Area", cheap_area)
        
        st.markdown("<br>", unsafe_allow_html=True)

        # ── TABS FOR DIRECTORY & ANALYTICS ──
        tab1, tab2 = st.tabs(["📋 PG Directory", "📈 Market Analytics"])

        # Tab 1: Data Table
        with tab1:
            cols = ["Name", "Location", "Sharing", "Gender", "Cost", "Rating", "Phone", "Comments"]
            st.dataframe(
                fdf[cols],
                column_config={
                    "Name":     st.column_config.TextColumn("PG Name", width="medium"),
                    "Cost":     st.column_config.NumberColumn("Rent/mo", format="₹%d"),
                    "Rating":   st.column_config.ProgressColumn("Rating", min_value=0, max_value=5, format="%.1f ⭐"),
                    "Comments": st.column_config.TextColumn("Reviews", width="large"),
                    "Phone":    st.column_config.TextColumn("Contact", width="medium"),
                },
                hide_index=True, 
                use_container_width=True, 
                height=650
            )

        # Tab 2: Visual Graphs & Analytics
        with tab2:
            st.caption(f"Visualizing structural characteristics for {len(fdf)} active matching records.")
            
            # Row 1: Distribution Analysis
            r1c1, r1c2 = st.columns(2)
            with r1c1:
                st.subheader("Price Distribution Spectrum")
                fig0 = px.histogram(fdf, x="Cost", nbins=15, color_discrete_sequence=["#1F77B4"], template="plotly_white")
                fig0.update_layout(
                    xaxis_title="Monthly Rental Tiers (₹)",
                    yaxis_title="Count of Accommodations",
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=360
                )
                st.plotly_chart(fig0, use_container_width=True)
                
            with r1c2:
                st.subheader("Room Config Allocation")
                sharing_counts = fdf["Sharing"].value_counts().reset_index()
                sharing_counts.columns = ["Sharing Type", "Count"]
                fig2 = px.pie(sharing_counts, names="Sharing Type", values="Count", hole=0.4,
                              color_discrete_sequence=CHART_THEME, template="plotly_white")
                fig2.update_traces(textposition='inside', textinfo='percent+label')
                fig2.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=360, showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)

            # Row 2: Location Pricing Strategy
            st.markdown("---")
            r2c1, r2c2 = st.columns(2)
            with r2c1:
                st.subheader("Mean Budget Thresholds by Area")
                area_cost = fdf.groupby("Location")["Cost"].mean().reset_index().sort_values("Cost", ascending=True)
                fig1 = px.bar(area_cost, x="Cost", y="Location", orientation='h', 
                              text=area_cost['Cost'].apply(lambda x: f"₹{int(x):,}"),
                              color="Cost", color_continuous_scale="Viridis", template="plotly_white")
                fig1.update_layout(xaxis_title="Average Rent (₹)", yaxis_title="", coloraxis_showscale=False, height=380,
                                   margin=dict(l=20, r=20, t=20, b=20))
                fig1.update_traces(textposition="outside")
                st.plotly_chart(fig1, use_container_width=True)
                
            with r2c2:
                st.subheader("Rent Variation & Dispersion Profile")
                fig4 = px.box(fdf, x="Location", y="Cost", color="Location", points="outliers",
                              color_discrete_sequence=CHART_THEME, template="plotly_white")
                fig4.update_layout(xaxis_title="", yaxis_title="Price Spread Range (₹)", showlegend=False, height=380,
                                   margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig4, use_container_width=True)

            # Row 3: Quality Scatter & Value Recommendation Engine
            st.markdown("---")
            r3c1, r3c2 = st.columns(2)
            with r3c1:
                st.subheader("Price vs. Community Rating Matrix")
                if not rated_pgs.empty:
                    fig3 = px.scatter(rated_pgs, x="Cost", y="Rating", color="Location", 
                                      hover_data=["Name", "Sharing"], opacity=0.75,
                                      color_discrete_sequence=CHART_THEME, template="plotly_white")
                    fig3.update_layout(xaxis_title="Monthly Cost Outlay (₹)", yaxis_title="Calculated Score (0-5)", height=360,
                                       margin=dict(l=20, r=20, t=20, b=20))
                    fig3.update_traces(marker=dict(size=12, line=dict(width=1, color='DarkSlateGrey')))
                    st.plotly_chart(fig3, use_container_width=True)
                else:
                    st.info("Insufficient feedback scores to plot a rating scatter index.")
                    
            with r3c2:
                st.subheader("🏆 Dynamic Value-for-Money Indexes")
                if not rated_pgs.empty:
                    val_df = rated_pgs.copy()
                    val_df["ValueScore"] = (val_df["Rating"] ** 2) / val_df["Cost"]
                    top_value = val_df.sort_values("ValueScore", ascending=False).head(5)
                    
                    st.dataframe(
                        top_value[["Name", "Location", "Sharing", "Cost", "Rating"]],
                        column_config={
                            "Name": "Accomodation Title",
                            "Cost": st.column_config.NumberColumn("Rent Rate", format="₹%d"),
                            "Rating": st.column_config.NumberColumn("Score", format="%.1f ⭐"),
                        },
                        hide_index=True, 
                        use_container_width=True,
                        height=260
                    )
                else:
                    st.info("Value optimizing metrics require rated entries.")


# ══════════════════════════════════════════════
#  PAGE 2: METRO MAP
# ══════════════════════════════════════════════
elif page == "🚇 Metro Map":
    df = load_data()
    st.title("🚇 Hyderabad Metro Network")
    st.write("Reference the official transit coordinates below to pair your daily commute with a nearby residency area.")
    st.link_button("Launch Interactive Transit Link ↗", "https://ltmetro.com/metro-network-map/")
    
    st.markdown("""
    ---
    ### 🚆 Core Route Networks
    * **🔴 Red Line:** Miyapur ↔ LB Nagar *(via Ameerpet, MGBS, Dilsukhnagar)*
    * **🔵 Blue Line:** Raidurg ↔ Nagole *(via HITEC City, Jubilee Hills, Ameerpet, Secunderabad)*
    * **🟢 Green Line:** JBS Parade Ground ↔ MG Bus Station *(via Musheerabad, RTC X Roads)*
    """)
    
    st.write("### 🗺️ Geographic Listing Overlays")
    if not df.empty:
        st.map(df[["lat", "lon"]], zoom=10, use_container_width=True)


# ══════════════════════════════════════════════
#  PAGE 3: ADD A PG & LINKS
# ══════════════════════════════════════════════
elif page == "➕ Add a PG & Info":
    st.title("➕ Contribute to the Database")
    st.write("This application runs directly on real crowdsourced community feedback.")

    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Submit your Review")
        st.link_button("Launch Submission Portal ↗", "https://docs.google.com/forms/d/e/1FAIpQLScXRf8vHeXwMeAbY_QLGDjGYemxD6BClUGffeOTTcra_9IBcQ/viewform")
        st.components.v1.iframe(
            "https://docs.google.com/forms/d/e/1FAIpQLScXRf8vHeXwMeAbY_QLGDjGYemxD6BClUGffeOTTcra_9IBcQ/viewform?embedded=true", 
            height=600, 
            scrolling=True
        )

    with col2:
        st.subheader("📊 Live Sheet Direct Link")
        st.link_button("Open Shared Google Sheet Rows ↗", "https://docs.google.com/spreadsheets/d/1AW4EKm412u_UyYhf1swdhDsP5ikadr3XXeUTMrqvh4w/edit")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("💬 Community Archives")
        st.markdown("""
        * 🧵 [Ultimate Hyderabad PG Database Thread](https://www.reddit.com/r/hyderabad/comments/1mzjwfj/lets_build_the_ultimate_hyderabad_pg_database/)
        * 🚀 [Project Launch Discussion Portal](https://www.reddit.com/r/hyderabad/comments/1ppxvnz/i_built_a_live_dashboard_to_find_pgs_in_hyderabad/)
        """)
