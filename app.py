import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Hyd Life: PG Finder",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ADVANCED DATA ENGINE ---

# Dictionary to map Area Names to approximate Lat/Lon for the Map View
# (Added the most common Hyderabad IT hubs)
LOCATION_COORDINATES = {
    "Gachibowli": [17.4401, 78.3489],
    "Madhapur": [17.4483, 78.3915],
    "Kondapur": [17.4622, 78.3568],
    "Hitec City": [17.4435, 78.3772],
    "Jubilee Hills": [17.4325, 78.4070],
    "Banjara Hills": [17.4123, 78.4389],
    "Kukatpally": [17.4948, 78.3996],
    "Manikonda": [17.4018, 78.3846],
    "Nanakramguda": [17.4125, 78.3396],
    "Hafeezpet": [17.4856, 78.3526],
    "Ameerpet": [17.4375, 78.4483],
    "Unknown": [17.3850, 78.4867] # General Hyd center
}

def generate_smart_tags(comment_text):
    """
    Scans reviews for keywords and assigns emoji tags.
    """
    tags = []
    text = str(comment_text).lower()
    
    # Positive keywords
    if any(x in text for x in ['good food', 'tasty', 'delicious']): tags.append("🍛 Good Food")
    if any(x in text for x in ['metro', 'transport', 'near']): tags.append("🚇 Metro Near")
    if any(x in text for x in ['clean', 'neat', 'maintained']): tags.append("✨ Clean")
    if any(x in text for x in ['fast', 'wifi', 'internet']): tags.append("🚀 Fast WiFi")
    
    # Negative keywords
    if any(x in text for x in ['bad food', 'worst food', 'repetitive']): tags.append("🥣 Bad Food")
    if any(x in text for x in ['cockroach', 'bugs', 'dirty']): tags.append("🪳 Hygiene Issue")
    if any(x in text for x in ['no parking', 'congested']): tags.append("🚫 No Parking")
    
    return tags if tags else ["📝 Reviewed"]

def clean_currency(x):
    if isinstance(x, str):
        clean_str = x.replace('₹', '').replace(',', '').strip()
        if '-' in clean_str:
            try:
                parts = clean_str.split('-')
                return (float(parts[0]) + float(parts[1])) / 2
            except: return 0
        try: return float(clean_str)
        except ValueError: return 0
    return x

@st.cache_data(ttl=600)
def load_data():
    try:
        # Live Google Sheet Link
        sheet_id = "1AW4EKm412u_UyYhf1swdhDsP5ikadr3XXeUTMrqvh4w"
        sheet_gid = "1856698473"
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={sheet_gid}"
        
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()

        column_mapping = {
            'Name of PG/Hostel:': 'Name',
            'Type of PG': 'Type',
            '🌍 Location:': 'Location',
            '🏡Type of Sharing:': 'Sharing',
            '💰 Monthly Cost (₹):': 'Cost',
            'Overall Rating:': 'Rating',
            'Additional Comments:': 'Comments',
            'PG Owner Phone number': 'Phone',
            'Contributor Gender': 'Gender'
        }
        df.rename(columns=column_mapping, inplace=True)

        # Cleaning
        df['Cost'] = df['Cost'].apply(clean_currency)
        df = df[(df['Cost'] > 2000) & (df['Cost'] < 60000)] # Realistic Range
        df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce').fillna(0)
        df['Location'] = df['Location'].fillna('Unknown').str.strip().str.title()
        df['Gender'] = df['Gender'].fillna('Any').str.strip()
        df['Comments'] = df['Comments'].fillna('')
        
        # --- ENRICHMENT ---
        # 1. Smart Tags
        df['Tags'] = df['Comments'].apply(generate_smart_tags)
        
        # 2. Coordinates
        # Map location string to lat/lon using our dictionary
        # If location not found, default to 'Unknown' coords
        coords = df['Location'].apply(lambda x: LOCATION_COORDINATES.get(x, LOCATION_COORDINATES.get(x.split(' ')[0], LOCATION_COORDINATES['Unknown'])))
        df['lat'] = coords.apply(lambda x: x[0])
        df['lon'] = coords.apply(lambda x: x[1])

        # 3. Value Score (Weighted: Rating matters more than just cheapness)
        # Score = (Rating^2) / Cost * 10000. 
        # This penalizes bad ratings heavily, even if cheap.
        df['Value Score'] = ((df['Rating'] ** 2) / df['Cost']) * 5000
        
        return df

    except Exception as e:
        st.error(f"Data Connection Error: {e}")
        return None

df = load_data()
if df is None: st.stop()

# --- 3. SIDEBAR CONTROLS ---
st.sidebar.title("🔍 Filter Your Stay")

# Dynamic Filters
loc_options = ["All"] + sorted(df['Location'].unique().tolist())
sel_loc = st.sidebar.selectbox("📍 Target Location", loc_options)

gender_options = ["All"] + sorted(df['Gender'].unique().tolist())
sel_gender = st.sidebar.selectbox("🚻 Gender", gender_options)

budget = st.sidebar.slider("💰 Max Budget (₹)", 
                           int(df['Cost'].min()), 
                           int(df['Cost'].max()), 
                           25000)

# Filter Logic
filtered_df = df.copy()
if sel_loc != "All": filtered_df = filtered_df[filtered_df['Location'] == sel_loc]
if sel_gender != "All": filtered_df = filtered_df[filtered_df['Gender'] == sel_gender]
filtered_df = filtered_df[filtered_df['Cost'] <= budget]

# --- 4. MAIN DASHBOARD UI ---

st.title("🏙️ Hyderabad PG Market Intelligence")
st.markdown("##### Real-time analysis of the rental market driven by community data.")

# Top Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Available PGs", len(filtered_df), delta=f"from {len(df)}")
m2.metric("Avg. Rent", f"₹{int(filtered_df['Cost'].mean()) if not filtered_df.empty else 0:,}")
m3.metric("Avg. Rating", f"{filtered_df['Rating'].mean():.1f} ⭐" if not filtered_df.empty else "0")
# Calculate 'Cheapest Area' dynamically
try:
    cheapest_area = filtered_df.groupby('Location')['Cost'].mean().idxmin()
except:
    cheapest_area = "-"
m4.metric("Cheapest Hub", cheapest_area)

st.markdown("---")

# TABS LAYOUT
tab1, tab2, tab3 = st.tabs(["📊 Market Analytics", "🏆 Find Recommendations", "🗺️ Map View"])

# --- TAB 1: ANALYTICS (VISUALS) ---
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Cost Distribution by Area")
        if not filtered_df.empty:
            # Using Plotly Box Plot for better statistical view
            fig_box = px.box(filtered_df, x="Location", y="Cost", color="Location",
                             points="all", hover_data=["Name", "Rating"],
                             title="Rent Ranges (Dots represent individual PGs)")
            st.plotly_chart(fig_box, use_container_width=True)
            
    with col2:
        st.subheader("Sharing Type Breakdown")
        if not filtered_df.empty:
            # Donut Chart
            fig_pie = px.pie(filtered_df, names='Sharing', values='Cost', hole=0.4,
                             title="Market Share by Room Type")
            st.plotly_chart(fig_pie, use_container_width=True)

    # Advanced Scatter: Rating vs Cost
    st.subheader("The Value Matrix: Rating vs. Cost")
    st.caption("Look for bubbles in the **Top-Left** (High Rating, Low Cost). Size = Value Score.")
    if not filtered_df.empty:
        fig_scatter = px.scatter(filtered_df, x="Cost", y="Rating", 
                                 size="Value Score", color="Location",
                                 hover_name="Name", hover_data=["Sharing", "Gender"],
                                 size_max=40)
        # Add a reference line for "Good Rating"
        fig_scatter.add_hline(y=4.0, line_dash="dash", line_color="green", annotation_text="Good Quality (>4.0)")
        st.plotly_chart(fig_scatter, use_container_width=True)

# --- TAB 2: RECOMMENDATIONS (ACTIONABLE) ---
with tab2:
    if not filtered_df.empty:
        # Get Top 3 based on 'Value Score'
        top_picks = filtered_df.sort_values(by='Value Score', ascending=False).head(3)
        
        st.write(f"### 🎯 We found {len(filtered_df)} PGs matching your criteria. Here are the Top 3:")
        
        # Display Cards
        for i, (index, row) in enumerate(top_picks.iterrows()):
            with st.container():
                # Card Styling
                c1, c2, c3 = st.columns([1, 2, 1])
                
                with c1:
                    st.markdown(f"## #{i+1}")
                    st.metric("Rating", f"{row['Rating']}⭐")
                
                with c2:
                    st.subheader(row['Name'])
                    st.markdown(f"📍 **{row['Location']}** | 🏠 {row['Sharing']}")
                    # Display Smart Tags as Pills
                    st.write(" ".join([f"`{tag}`" for tag in row['Tags']]))
                    if row['Comments']:
                        st.caption(f"💬 \"{row['Comments'][:100]}...\"")

                with c3:
                    st.markdown(f"### ₹{int(row['Cost']):,}")
                    st.button(f"Show Phone", key=f"btn_{index}", help=str(row['Phone']))
                
                st.divider()
    else:
        st.warning("No PGs match your filters. Try increasing the budget!")

# --- TAB 3: MAP VIEW (GEOSPATIAL) ---
with tab3:
    st.subheader("📍 Geolocation of PGs")
    st.markdown("Note: Locations are approximate based on Area center points.")
    
    if not filtered_df.empty:
        # Streamlit Map needs columns named 'lat' and 'lon'
        map_data = filtered_df[['lat', 'lon']].copy()
        
        # Add some random jitter so points don't stack perfectly on top of each other
        # (Since all Gachibowli points have same center, this separates them visually)
        map_data['lat'] = map_data['lat'] + np.random.normal(0, 0.002, len(map_data))
        map_data['lon'] = map_data['lon'] + np.random.normal(0, 0.002, len(map_data))
        
        st.map(map_data, zoom=11)
    else:
        st.info("No data to map.")

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: grey;'>
    Data Source: Reddit Hyderabad Community • Built with Python & Streamlit • <a href='https://github.com/prosuvinhere/Hyd_PG'>Star on GitHub</a>
</div>
""", unsafe_allow_html=True)
