import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set the page configuration for a wider layout
st.set_page_config(layout="wide")

# --- Data Loading ---
# Load the data from the external CSV file
try:
    df = pd.read_csv("pg_data.csv")
except FileNotFoundError:
    st.error("Error: The data file 'pg_data.csv' was not found. Please make sure it's in the same directory as the app.")
    st.stop() # Stop the app from running further

# --- Data Cleaning ---
# First, strip whitespace from column names
df.columns = df.columns.str.strip()

# Rename columns for easier handling
column_mapping = {
    'Name of PG/Hostel:': 'Name',
    'Type of PG': 'Type',
    '🌍 Location:': 'Location',
    '🏡Type of Sharing:': 'Sharing',
    '💰 Monthly Cost (₹):': 'Cost',
    '🍴 Food Quality:': 'Food Quality',
    '🚲Parking Space': 'Parking',
    '🏢 Room Space:': 'Room Space',
    '⚡Electricity Bill:': 'Electricity',
    'Overall Rating:': 'Overall Rating',
    'Additional Comments:': 'Comments',
    'Contributor Reddit Username': 'Contributor',
    'PG Owner Phone number': 'Phone',
    'Contributor Gender': 'Gender'
}
df.rename(columns=column_mapping, inplace=True)

# Clean data
df['Phone'] = df['Phone'].fillna('N/A')
df['Cost'] = pd.to_numeric(df['Cost'], errors='coerce').fillna(0).astype(int)
df['Gender'] = df['Gender'].fillna('Not Specified')
df['Location'] = df['Location'].fillna('Unknown')
df['Sharing'] = df['Sharing'].fillna('Unknown')
df['Overall Rating'] = pd.to_numeric(df['Overall Rating'], errors='coerce').fillna(0)

# Hide Timestamp column if it exists
if 'Timestamp' in df.columns:
    df = df.drop('Timestamp', axis=1)

# --- Streamlit App UI ---
st.title("🏡 Hyderabad PG/Hostel Information")
st.markdown("A crowd-sourced list of PGs and Hostels in and around Hyderabad. Use the filters in the sidebar to narrow down your search and update the charts.")

# --- Sidebar Filters ---
st.sidebar.header("🔎 Filter Options")

# Location Filter
locations = sorted(df['Location'].unique())
selected_locations = st.sidebar.multiselect("📍 Location", locations, default=locations)

# Gender Filter
genders = sorted(df['Gender'].unique())
selected_genders = st.sidebar.multiselect("🚻 Gender", genders, default=genders)

# Type of PG Filter
pg_types = sorted(df['Type'].unique())
selected_pg_types = st.sidebar.multiselect("🏠 Type of PG", pg_types, default=pg_types)

# Cost Filter
min_cost, max_cost = int(df['Cost'].min()), int(df['Cost'].max())
selected_cost_range = st.sidebar.slider(
    "💰 Monthly Cost (₹)",
    min_value=min_cost,
    max_value=max_cost,
    value=(min_cost, max_cost)
)

# --- Filtering Logic ---
filtered_df = df[
    (df['Location'].isin(selected_locations)) &
    (df['Gender'].isin(selected_genders)) &
    (df['Type'].isin(selected_pg_types)) &
    (df['Cost'] >= selected_cost_range[0]) &
    (df['Cost'] <= selected_cost_range[1])
].copy()


# --- Display Filtered Table ---
st.header(f"Displaying {len(filtered_df)} of {len(df)} PG/Hostels")
st.dataframe(filtered_df, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)


# --- Visual Insights Section ---
st.header("📊 Visual Insights")
st.markdown("These charts are updated based on your filter selections above.")

if filtered_df.empty:
    st.warning("No data matches the current filters. Please broaden your selection to see insights.")
else:
    # --- Create two columns for charts ---
    col1, col2 = st.columns(2)

    with col1:
        # --- Chart 1: Average Cost by Location ---
        st.subheader("Average Cost by Location")
        avg_cost_location = filtered_df.groupby('Location')['Cost'].mean().sort_values(ascending=False).round(0)
        st.bar_chart(avg_cost_location)

        # --- Chart 2: Average Cost by Sharing Type ---
        st.subheader("Average Cost by Sharing Type")
        avg_cost_sharing = filtered_df.groupby('Sharing')['Cost'].mean().sort_values(ascending=False).round(0)
        st.bar_chart(avg_cost_sharing)


    with col2:
        # --- Chart 3: Accommodation Counts by Location ---
        st.subheader("Accommodation Counts by Location")
        location_counts = filtered_df['Location'].value_counts()
        st.bar_chart(location_counts)

        # --- Chart 4: Overall Rating vs. Monthly Cost ---
        st.subheader("Rating vs. Cost")
        # Use Matplotlib for the scatter plot
        fig, ax = plt.subplots()
        sns.scatterplot(
            data=filtered_df,
            x='Cost',
            y='Overall Rating',
            hue='Sharing',
            ax=ax
        )
        ax.set_title("Overall Rating vs. Monthly Cost")
        ax.set_xlabel("Monthly Cost (₹)")
        ax.set_ylabel("Overall Rating")
        ax.grid(True, linestyle='--', alpha=0.6)
        st.pyplot(fig)


st.markdown("---")
st.info("All thanks to https://www.reddit.com/user/thedesimonk/")
st.markdown("⭐ If you find this helpful, please star the [GitHub repo](https://github.com/prosuvinhere/Hyd_PG)!")
