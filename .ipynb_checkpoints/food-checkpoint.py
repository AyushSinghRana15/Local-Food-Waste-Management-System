import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ---  Connect to DB ---
conn = sqlite3.connect("local_food_wastage.db")
cursor = conn.cursor()

# Auto-update status for expired items
conn.execute("""
UPDATE Food_Listings
SET status = 'Expired'
WHERE date(expiry) < date('now') AND status = 'Available';
""")
conn.commit()

# ---  Import Queries Dictionary ---
from queries_dict import queries   # make sure queries_dict.py is present with your queries dictionary

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
st.sidebar.header("🛠️ Manage Food Listings")

# CRUD menu in sidebar
crud_menu = st.sidebar.selectbox("Choose Action", ["View Entries", "Add Entry", "Update Entry", "Delete Entry", "Analytics & Reports"])

if crud_menu != "Analytics & Reports":
    if crud_menu == "View Entries":
        st.subheader("All Food Listings")
        df = pd.read_sql("SELECT * FROM Food_Listings", conn)
        st.dataframe(df)

    elif crud_menu == "Add Entry":
        st.subheader("Add New Food Entry")
        with st.form("add_form"):
            food_name = st.text_input("Food Name")
            quantity = st.number_input("Quantity", min_value=1)
            expiry = st.date_input("Expiry Date", datetime.today())
            provider_id = st.number_input("Provider ID", min_value=1)
            location = st.text_input("Location")
            food_type = st.text_input("Food Type")
            status = st.selectbox("Status", ["Available", "Claimed", "Expired"])

            submitted = st.form_submit_button("Add Food")
            if submitted:
                cursor.execute("""
                    INSERT INTO Food_Listings 
                    (food_name, quantity, expiry, provider_id, location, food_type, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (food_name, quantity, expiry.strftime('%Y-%m-%d'), provider_id, location, food_type, status)
                )
                conn.commit()
                st.success(f"Food '{food_name}' added successfully!")

    elif crud_menu == "Update Entry":
        st.subheader("Update Food Entry")
        food_id = st.number_input("Food ID to Update", min_value=1)
        existing = pd.read_sql(f"SELECT * FROM Food_Listings WHERE food_id={food_id}", conn)
        if existing.empty:
            st.error("Food ID not found.")
        else:
            row = existing.iloc[0]
            with st.form("update_form"):
                food_name = st.text_input("Food Name", value=row['food_name'])
                quantity = st.number_input("Quantity", min_value=1, value=int(row['quantity']))
                expiry = st.date_input("Expiry Date", value=pd.to_datetime(row['expiry']))
                provider_id = st.number_input("Provider ID", min_value=1, value=int(row['provider_id']))
                location = st.text_input("Location", value=row['location'])
                food_type = st.text_input("Food Type", value=row['food_type'])
                status = st.selectbox("Status", ["Available", "Claimed", "Expired"], index=["Available", "Claimed", "Expired"].index(row['status']))

                submitted = st.form_submit_button("Update Food")
                if submitted:
                    cursor.execute("""
                        UPDATE Food_Listings SET 
                        food_name = ?, quantity = ?, expiry = ?, provider_id = ?, location = ?, food_type = ?, status = ?
                        WHERE food_id = ?""",
                        (food_name, quantity, expiry.strftime('%Y-%m-%d'), provider_id, location, food_type, status, food_id)
                    )
                    conn.commit()
                    st.success(f"Food ID {food_id} updated successfully!")

    elif crud_menu == "Delete Entry":
        st.subheader("Delete Food Entry")
        food_id = st.number_input("Food ID to Delete", min_value=1)
        if st.button("Delete"):
            cursor.execute("DELETE FROM Food_Listings WHERE food_id = ?", (food_id,))
            conn.commit()
            st.warning(f"Food ID {food_id} deleted if it existed.")

else:
    # --- Sidebar Filters for Analytics ---
    st.sidebar.header("🔍 Filters")

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



conn.close()
