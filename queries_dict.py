# Dictionary of SQL queries for the Local Food Wastage Management System

queries = {
    # 1. All available food
    "available_food": """
        SELECT f.food_id, f.food_name, f.quantity, f.expiry, f.location, 
               f.food_type, f.meal_type, p.name AS provider_name, p.contact
        FROM Food_Listings f
        JOIN Providers p ON f.provider_id = p.provider_id
        WHERE f.status = 'Available'
        ORDER BY f.expiry ASC;
    """,

    # 2. Claimed food with receiver details
    "claimed_food": """
        SELECT f.food_id, f.food_name, f.quantity, f.location, f.food_type, 
               r.name AS receiver_name, r.contact, c.claim_time
        FROM Claims c
        JOIN Food_Listings f ON c.food_id = f.food_id
        JOIN Receivers r ON c.receiver_id = r.receiver_id
        ORDER BY c.claim_time DESC;
    """,

    # 3. Expired food
    "expired_food": """
        SELECT food_id, food_name, quantity, expiry, location, food_type, meal_type
        FROM Food_Listings
        WHERE status = 'Expired'
        ORDER BY expiry DESC;
    """,

    # 4. Available food by city
    "available_by_city": """
        SELECT location, COUNT(*) AS total_items, SUM(quantity) AS total_quantity
        FROM Food_Listings
        WHERE status = 'Available'
        GROUP BY location
        ORDER BY total_quantity DESC;
    """,

    # 5. Available food by provider type
    "available_by_provider_type": """
        SELECT provider_type, COUNT(*) AS total_items, SUM(quantity) AS total_quantity
        FROM Food_Listings
        WHERE status = 'Available'
        GROUP BY provider_type
        ORDER BY total_quantity DESC;
    """,

    # 6. Food near expiry (next 24 hours)
    "near_expiry": """
        SELECT food_id, food_name, quantity, expiry, location, provider_id
        FROM Food_Listings
        WHERE status = 'Available' 
        AND date(expiry) <= date('now', '+1 day')
        ORDER BY expiry ASC;
    """,

    # 7. Top 5 providers by quantity donated
    "top_providers": """
        SELECT p.name AS provider_name, SUM(f.quantity) AS total_quantity
        FROM Food_Listings f
        JOIN Providers p ON f.provider_id = p.provider_id
        GROUP BY p.name
        ORDER BY total_quantity DESC
        LIMIT 5;
    """,

    # 8. Top 5 receivers by quantity claimed
    "top_receivers": """
        SELECT r.name AS receiver_name, SUM(f.quantity) AS total_claimed
        FROM Claims c
        JOIN Food_Listings f ON c.food_id = f.food_id
        JOIN Receivers r ON c.receiver_id = r.receiver_id
        GROUP BY r.name
        ORDER BY total_claimed DESC
        LIMIT 5;
    """,

    # 9. Food wastage by location & type
    "wastage_by_location_type": """
        SELECT location, food_type, COUNT(*) AS total_items, SUM(quantity) AS total_quantity
        FROM Food_Listings
        WHERE status = 'Expired'
        GROUP BY location, food_type
        ORDER BY total_quantity DESC;
    """,

    # 10. Claimed vs expired quantity summary
    "claimed_vs_expired": """
        SELECT status, COUNT(*) AS total_items, SUM(quantity) AS total_quantity
        FROM Food_Listings
        WHERE status IN ('Claimed', 'Expired')
        GROUP BY status;
    """,

    # 11. Monthly food donations trend
    "monthly_donations": """
        SELECT strftime('%Y-%m', expiry) AS month,
               COUNT(*) AS items_listed,
               SUM(quantity) AS quantity_listed
        FROM Food_Listings
        GROUP BY month
        ORDER BY month ASC;
    """,

    # 12. Monthly food claims trend
    "monthly_claims": """
        SELECT strftime('%Y-%m', claim_time) AS month,
               COUNT(*) AS items_claimed,
               SUM(f.quantity) AS quantity_claimed
        FROM Claims c
        JOIN Food_Listings f ON c.food_id = f.food_id
        GROUP BY month
        ORDER BY month ASC;
    """,

    # 13. Filtered available food (dynamic replacements in Streamlit)
    "filtered_available_food": """
        SELECT f.food_id, f.food_name, f.quantity, f.expiry, f.location, 
               f.food_type, f.meal_type, p.name AS provider_name, p.contact
        FROM Food_Listings f
        JOIN Providers p ON f.provider_id = p.provider_id
        WHERE f.status = 'Available'
          AND (:city = 'All' OR f.location = :city)
          AND (:food_type = 'All' OR f.food_type = :food_type)
          AND (:meal_type = 'All' OR f.meal_type = :meal_type)
        ORDER BY f.expiry ASC;
    """,

    # 14. Provider contact list for available food
    "provider_contacts_for_available": """
        SELECT DISTINCT p.name AS provider_name, p.contact, f.location, f.food_type
        FROM Food_Listings f
        JOIN Providers p ON f.provider_id = p.provider_id
        WHERE f.status = 'Available'
        ORDER BY p.name;
    """,

    # 15. Summary dashboard data
    "dashboard_summary": """
        SELECT 
            (SELECT COUNT(*) FROM Food_Listings WHERE status = 'Available') AS available_count,
            (SELECT SUM(quantity) FROM Food_Listings WHERE status = 'Available') AS available_quantity,
            (SELECT COUNT(*) FROM Food_Listings WHERE status = 'Expired') AS expired_count,
            (SELECT SUM(quantity) FROM Food_Listings WHERE status = 'Expired') AS expired_quantity,
            (SELECT COUNT(*) FROM Food_Listings WHERE status = 'Claimed') AS claimed_count,
            (SELECT SUM(quantity) FROM Food_Listings WHERE status = 'Claimed') AS claimed_quantity;
    """
}
