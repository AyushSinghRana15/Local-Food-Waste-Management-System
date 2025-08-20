import streamlit as st
import pandas as pd
import sqlite3

# ---  Connect to DB ---
conn = sqlite3.connect("local_food_wastage.db")

# Auto-update status for expired items
conn.execute("""
UPDATE Food_Listings
SET status = 'Expired'
WHERE date(expiry) < date('now') AND status = 'Available';
""")
conn.commit()

# ---  Import Queries Dictionary ---
from queries_dict import queries   # Import the dictionary from a separate file

# ---  ---  Page Config ---
st.set_page_config(
    page_title="🍲 Local Food Wastage Management System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---  Custom CSS Styling ---
st.markdown("""
    <style>
        .main {
            background-color: #f8f9fa;
        }
        .stTabs [role="tablist"] {
            justify-content: center;
        }
        table {
            border-radius: 8px;
            overflow: hidden;
        }
        th {
            background-color: #4CAF50 !important;
            color: white !important;
        }
        td {
            background-color: #ffffff;
        }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")

# Dynamic filter values from database
locations = ["All"] + list(pd.read_sql("SELECT DISTINCT location FROM Food_Listings", conn)['location'])
food_types = ["All"] + list(pd.read_sql("SELECT DISTINCT food_type FROM Food_Listings", conn)['food_type'])
meal_types = ["All"] + list(pd.read_sql("SELECT DISTINCT meal_type FROM Food_Listings", conn)['meal_type'])
provider_types = ["All"] + list(pd.read_sql("SELECT DISTINCT provider_type FROM Food_Listings", conn)['provider_type'])

city_filter = st.sidebar.selectbox("🌆 City", locations)
food_filter = st.sidebar.selectbox("🥗 Food Type", food_types)
meal_filter = st.sidebar.selectbox("🍛 Meal Type", meal_types)
prov_type_filter = st.sidebar.selectbox("🏢 Provider Type", provider_types)

# --- Tabs for Each Query ---
tab_titles = [
    "Available Food", "Claimed Food", "Expired Food", "Available by City", 
    "Available by Provider Type", "Near Expiry (24h)", "Top Providers", "Top Receivers",
    "Wastage by Location & Type", "Claimed vs Expired Summary", "Monthly Donations Trend",
    "Monthly Claims Trend", "Filtered Available Food", "Provider Contacts", "Dashboard Summary"
]

tabs = st.tabs(tab_titles)

# --- Tab 1: All Available Food ---
with tabs[0]:
    st.subheader("🥗 Currently Available Food Items")
    df = pd.read_sql(queries["available_food"], conn)
    st.dataframe(df, use_container_width=True)

# --- Tab 2: Claimed Food ---
with tabs[1]:
    st.subheader("📦 Claimed Food and Receiver Details")
    df = pd.read_sql(queries["claimed_food"], conn)
    st.dataframe(df, use_container_width=True)

# --- Tab 3: Expired Food ---
with tabs[2]:
    st.subheader("⏳ Expired Food Items")
    df = pd.read_sql(queries["expired_food"], conn)
    st.dataframe(df, use_container_width=True)

# --- Tab 4: Available Food by City ---
with tabs[3]:
    st.subheader("🏙 Available Food by City")
    df = pd.read_sql(queries["available_by_city"], conn)
    st.bar_chart(df.set_index("location")["total_quantity"])
    st.dataframe(df, use_container_width=True)

# --- Tab 5: Available Food by Provider Type ---
with tabs[4]:
    st.subheader("🏢 Available Food by Provider Type")
    df = pd.read_sql(queries["available_by_provider_type"], conn)
    st.bar_chart(df.set_index("provider_type")["total_quantity"])
    st.dataframe(df, use_container_width=True)

# --- Tab 6: Food Near Expiry ---
with tabs[5]:
    st.subheader("⚠ Near Expiry Food Items (Next 24 Hours)")
    df = pd.read_sql(queries["near_expiry"], conn)
    st.dataframe(df, use_container_width=True)

# --- Tab 7: Top Providers ---
with tabs[6]:
    st.subheader("🏆 Top Providers by Quantity Donated")
    df = pd.read_sql(queries["top_providers"], conn)
    st.bar_chart(df.set_index("provider_name")["total_quantity"])
    st.dataframe(df, use_container_width=True)

# --- Tab 8: Top Receivers ---
with tabs[7]:
    st.subheader("🤝 Top Receivers by Quantity Claimed")
    df = pd.read_sql(queries["top_receivers"], conn)
    st.bar_chart(df.set_index("receiver_name")["total_claimed"])
    st.dataframe(df, use_container_width=True)

# --- Tab 9: Wastage by Location & Type ---
with tabs[8]:
    st.subheader("♻ Wastage by Location and Food Type")
    df = pd.read_sql(queries["wastage_by_location_type"], conn)
    st.dataframe(df, use_container_width=True)

# --- Tab 10: Claimed vs Expired ---
with tabs[9]:
    st.subheader("📊 Claimed vs Expired Summary")
    df = pd.read_sql(queries["claimed_vs_expired"], conn)
    st.bar_chart(df.set_index("status")["total_quantity"])
    st.dataframe(df, use_container_width=True)

# --- Tab 11: Monthly Donations ---
with tabs[10]:
    st.subheader("📅 Monthly Food Donations Trend")
    df = pd.read_sql(queries["monthly_donations"], conn)
    st.line_chart(df.set_index("month")["quantity_listed"])
    st.dataframe(df, use_container_width=True)

# --- Tab 12: Monthly Claims ---
with tabs[11]:
    st.subheader("📅 Monthly Claims Trend")
    df = pd.read_sql(queries["monthly_claims"], conn)
    st.line_chart(df.set_index("month")["quantity_claimed"])
    st.dataframe(df, use_container_width=True)

# --- Tab 13: Filtered Available Food ---
with tabs[12]:
    st.subheader("🔍 Filtered Available Food")
    filters = ["f.status = 'Available'"]  # Base condition

    if city_filter != "All":
        filters.append(f"f.location = '{city_filter}'")
    if food_filter != "All":
        filters.append(f"f.food_type = '{food_filter}'")
    if meal_filter != "All":
        filters.append(f"f.meal_type = '{meal_filter}'")
    if prov_type_filter != "All":
        # IMPORTANT → provider_type exists in Food_Listings, not Providers
        filters.append(f"f.provider_type = '{prov_type_filter}'")

    where_clause = " AND ".join(filters)
    query = f"""
        SELECT f.food_id, f.food_name, f.quantity, f.expiry, f.location, 
               f.food_type, f.meal_type, p.name AS provider_name, p.contact
        FROM Food_Listings f
        JOIN Providers p ON f.provider_id = p.provider_id
        WHERE f.status = 'Available'
        {'AND f.location="' + city_filter + '"' if city_filter != 'All' else ''}
        {'AND f.food_type="' + food_filter + '"' if food_filter != 'All' else ''}
        {'AND f.meal_type="' + meal_filter + '"' if meal_filter != 'All' else ''}
        {'AND f.provider_type="' + prov_type_filter + '"' if prov_type_filter != 'All' else ''}
        ORDER BY f.expiry ASC;
    """
    df = pd.read_sql(query, conn)
    st.dataframe(df, use_container_width=True)

# --- Tab 14: Provider Contacts ---
with tabs[13]:
    st.subheader("☎ Provider Contact List")
    df = pd.read_sql(queries["provider_contacts_for_available"], conn)
    st.dataframe(df, use_container_width=True)

# --- Tab 15: Dashboard Summary ---
with tabs[14]:
    st.subheader("📊 Dashboard Summary")
    df = pd.read_sql(queries["dashboard_summary"], conn)
    st.metric(label="Available Items", value=df['available_count'][0])
    st.metric(label="Available Quantity", value=df['available_quantity'][0])
    st.metric(label="Expired Items", value=df['expired_count'][0])
    st.metric(label="Expired Quantity", value=df['expired_quantity'][0])
    st.metric(label="Claimed Items", value=df['claimed_count'][0])
    st.metric(label="Claimed Quantity", value=df['claimed_quantity'][0])

