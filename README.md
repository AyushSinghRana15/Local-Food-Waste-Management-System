# Local Food Wastage Management System

## Project Description
The Local Food Wastage Management System is an end-to-end digital platform designed to address the critical issue of food wastage by efficiently connecting food providers (such as restaurants, grocery stores, and individuals) with receivers (like NGOs and those in need). The system facilitates real-time tracking of surplus food donations, including detailed information on quantities, expiry dates, and locations.

This solution leverages an SQLite database to store and manage food listings, providers, receivers, and claims data. With a user-friendly Streamlit-based web interface, it enables easy food inventory filtering, claiming, and management. The project incorporates robust CRUD operations to add, update, and delete food entries, ensuring dynamic and accurate data handling.

Advanced data analysis and visualization features provide actionable insights into food wastage trends by category, location, and time, empowering stakeholders to make informed decisions that reduce wastage and improve food redistribution. By bridging the gap between surplus food and recipients, this system contributes to community welfare and environmental sustainability.

## Features
- Real-time food inventory management with status updates (Available, Claimed, Expired)
- Easy addition, modification, and deletion of food listings via CRUD operations
- Filtering and searching food by city, food type, meal type, and provider type
- Interactive dashboard with metrics, charts, and tables showing wastage trends and activity summaries
- Provider contact information for streamlined communication and coordination
- Automated status update for expired food items based on expiry dates

## Technologies Used
- Python 3
- SQLite for lightweight database management
- Pandas for data processing and analysis
- Streamlit for building the interactive web interface
- SQL for querying food wastage trends and inventory management

## Installation and Usage
1. Clone the repository
2. Install dependencies (`streamlit`, `pandas`, `sqlite3`, etc.)
3. Run the Streamlit app with:  

streamlit run your_app_file.py

4. Use the sidebar to manage food listings or explore food wastage analytics in interactive tabs.

## Future Enhancements
- Integration with mobile apps for easier onboarding and claiming
- Incorporation of AI to predict wastage and optimize distribution
- Improved user roles and authentication
- Support for multiple languages and regions

---

This project demonstrates practical applications of database management, web UI design, and data-driven decision making toward reducing food wastage and promoting sustainability.
