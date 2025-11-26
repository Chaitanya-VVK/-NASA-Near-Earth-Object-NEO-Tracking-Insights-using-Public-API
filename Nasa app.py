import streamlit as st
import pandas as pd
import mysql.connector
from datetime import date

# ---------------------------------------------------------
# Page config
# ---------------------------------------------------------
st.set_page_config(page_title="NASA Asteroid Tracker", layout="wide")

# Theme override
st.markdown("""
<style>
.stSlider > div[data-baseweb="slider"] > div > div {
    background: #f7c6d4 !important;
}
.stSlider > div[data-baseweb="slider"] > div > div > div {
    background: #9bb1ff !important;
}
.stSlider > div[data-baseweb="slider"] div div span {
    background: #6b7cff !important;
    border: 2px solid #4a58ff !important;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# DB helper
# ---------------------------------------------------------
def run_query(sql: str) -> pd.DataFrame:
    """Open a fresh MySQL connection, run query, return DataFrame."""
    conn = mysql.connector.connect(
        host="localhost",
        user="your User name",
        password="your DB PWD",       # 🔁 change if your password is different
        database="neo_data"
    )
    df = pd.read_sql(sql, conn)
    conn.close()
    return df

# ---------------------------------------------------------
# Main title
# ---------------------------------------------------------
st.title("🚀 NASA Asteroid Tracker")
st.markdown("""
<style>
h1 {
    color: #4834d4 !important;  /* Soft violet */
    text-align: center;
    font-weight: 900;
}
</style>
""", unsafe_allow_html=True)
st.write("Welcome! Use the sidebar to navigate.")

# ---------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------
st.sidebar.title("Asteroid Approaches")
page = st.sidebar.radio("Go to", ["Filter Criteria","Queries"])

# =========================================================
# QUERIES PAGE
# =========================================================
if page == "Queries":
    st.header("📊 SQL Query Explorer")

    query_list = [
        "1. Count how many times each asteroid has approached Earth",
        "2. Average velocity of each asteroid over multiple approaches",
        "3. List top 10 fastest asteroids",
        "4. Potentially hazardous asteroids with more than 3 approaches",
        "5. Month with the most asteroid approaches",
        "6. Asteroid with the fastest ever approach speed",
        "7. Sort asteroids by maximum estimated diameter (descending)",
        "8. Approaches ordered by asteroid and date (see getting closer over time)",
        "9. Closest approach (date & miss distance) for each asteroid",
        "10. Asteroids with velocity > 50,000 km/h",
        "11. Count how many approaches happened per month",
        "12. Asteroids with highest brightness (lowest magnitude)",
        "13. Number of hazardous vs non-hazardous asteroids",
        "14. Asteroids that passed closer than the Moon (< 1 LD)",
        "15. Asteroids that came within 0.05 AU"
    ]

    choice = st.selectbox(
        "Select your query", 
        query_list,
        index=None,
        placeholder="Choose an option")

    # ----------------- Query 1 -----------------
    if choice == query_list[0]:
        sql = """
            SELECT asteroid_id,
                   COUNT(*) AS approach_count
            FROM close_approach
            GROUP BY asteroid_id
            ORDER BY approach_count DESC;
        """
        st.dataframe(run_query(sql))

    # ----------------- Query 2 -----------------
    if choice == query_list[1]:
        sql = """
            SELECT asteroid_id,
                   AVG(relative_velocity_kmph) AS avg_velocity_kmph
            FROM close_approach
            GROUP BY asteroid_id
            ORDER BY avg_velocity_kmph DESC;
        """
        st.dataframe(run_query(sql))

    # ----------------- Query 3 -----------------
    if choice == query_list[2]:
        sql = """
            SELECT a.name,
                   MAX(c.relative_velocity_kmph) AS max_velocity_kmph
            FROM close_approach c
            JOIN asteroids a ON a.asteroid_id = c.asteroid_id
            GROUP BY a.asteroid_id, a.name
            ORDER BY max_velocity_kmph DESC
            LIMIT 10;
        """
        st.dataframe(run_query(sql))

    # ----------------- Query 4 -----------------
    if choice == query_list[3]:
        sql = """
            SELECT a.name,
                   COUNT(*) AS approach_count
            FROM close_approach c
            JOIN asteroids a ON a.asteroid_id = c.asteroid_id
            WHERE a.is_potentially_hazardous_asteroid = 1
            GROUP BY a.asteroid_id, a.name
            HAVING COUNT(*) > 3
            ORDER BY approach_count DESC;
        """
        st.dataframe(run_query(sql))

    # ----------------- Query 5 -----------------
    if choice == query_list[4]:
        sql = """
            SELECT DATE_FORMAT(close_approach_date, '%Y-%m') AS year_month,
                   COUNT(*) AS total_approaches
            FROM close_approach
            GROUP BY year_month
            ORDER BY total_approaches DESC
            LIMIT 1;
        """
        st.dataframe(run_query(sql))

    # ----------------- Query 6 -----------------
    if choice == query_list[5]:
        sql = """
            SELECT a.name,
                   c.relative_velocity_kmph,
                   c.close_approach_date
            FROM close_approach c
            JOIN asteroids a ON a.asteroid_id = c.asteroid_id
            ORDER BY c.relative_velocity_kmph DESC
            LIMIT 1;
        """
        st.dataframe(run_query(sql))

    # ----------------- Query 7 -----------------
    if choice == query_list[6]:
        sql = """
            SELECT name,
                   estimated_diameter_max_km
            FROM asteroids
            ORDER BY estimated_diameter_max_km DESC;
        """
        st.dataframe(run_query(sql))

    # ----------------- Query 8 -----------------
    if choice == query_list[7]:
        sql = """
            SELECT asteroid_id,
                   close_approach_date,
                   miss_distance_km
            FROM close_approach
            ORDER BY asteroid_id, close_approach_date;
        """
        st.dataframe(run_query(sql))

    # ----------------- Query 9 -----------------
    if choice == query_list[8]:
        sql = """
            SELECT a.name,
                   c.close_approach_date,
                   c.miss_distance_km
            FROM close_approach c
            JOIN asteroids a ON a.asteroid_id = c.asteroid_id
            JOIN (
                SELECT asteroid_id,
                       MIN(miss_distance_km) AS min_dist
                FROM close_approach
                GROUP BY asteroid_id
            ) m
              ON c.asteroid_id = m.asteroid_id
             AND c.miss_distance_km = m.min_dist
            ORDER BY c.miss_distance_km ASC;
        """
        st.dataframe(run_query(sql))

    # ----------------- Query 10 -----------------
    if choice == query_list[9]:
        sql = """
            SELECT DISTINCT a.name,
                            c.relative_velocity_kmph,
                            c.close_approach_date
            FROM close_approach c
            JOIN asteroids a ON a.asteroid_id = c.asteroid_id
            WHERE c.relative_velocity_kmph > 50000
            ORDER BY c.relative_velocity_kmph DESC;
        """
        st.dataframe(run_query(sql))

    # ----------------- Query 11 -----------------
    if choice == query_list[10]:
        sql = """
            SELECT DATE_FORMAT(close_approach_date, '%Y-%m') AS year_month,
                   COUNT(*) AS total_approaches
            FROM close_approach
            GROUP BY year_month
            ORDER BY year_month;
        """
        st.dataframe(run_query(sql))

    # ----------------- Query 12 -----------------
    if choice == query_list[11]:
        sql = """
            SELECT name,
                   absolute_magnitude_h
            FROM asteroids
            ORDER BY absolute_magnitude_h ASC
            LIMIT 10;
        """
        st.dataframe(run_query(sql))

    # ----------------- Query 13 -----------------
    if choice == query_list[12]:
        sql = """
            SELECT is_potentially_hazardous_asteroid AS hazardous_flag,
                   COUNT(*) AS total
            FROM asteroids
            GROUP BY is_potentially_hazardous_asteroid;
        """
        st.dataframe(run_query(sql))

    # ----------------- Query 14 -----------------
    if choice == query_list[13]:
        sql = """
            SELECT a.name,
                   c.close_approach_date,
                   c.miss_distance_lunar
            FROM close_approach c
            JOIN asteroids a ON a.asteroid_id = c.asteroid_id
            WHERE c.miss_distance_lunar < 1
            ORDER BY c.miss_distance_lunar ASC;
        """
        st.dataframe(run_query(sql))

    # ----------------- Query 15 -----------------
    if choice == query_list[14]:
        sql = """
            SELECT a.name,
                   c.close_approach_date,
                   c.astronomical
            FROM close_approach c
            JOIN asteroids a ON a.asteroid_id = c.asteroid_id
            WHERE c.astronomical < 0.05
            ORDER BY c.astronomical ASC;
        """
        st.dataframe(run_query(sql))

# =========================================================
# FILTER CRITERIA PAGE
# =========================================================
if page == "Filter Criteria":
    st.header("🔍 Filter Asteroids")

    # ----------- Inputs -----------
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=date(2024, 1, 1))
    with col2:
        end_date = st.date_input("End Date", value=date(2025, 12, 31))

    vel_min, vel_max = st.slider(
        "Relative velocity (km/h)",
        0.0, 150000.0, (0.0, 150000.0)
    )

    dia_min, dia_max = st.slider(
        "Estimated Diameter (km)",
        0.0, 20.0, (0.0, 20.0)
    )

    au_min, au_max = st.slider(
        "Astronomical Units (AU)",
        0.0, 5.0, (0.0, 5.0)
    )

    ld_min, ld_max = st.slider(
        "Lunar Distance (LD)",
        0.0, 10.0, (0.0, 10.0)
    )

    hazard_option = st.selectbox(
        "Only show potentially hazardous?",
        ["All", "Hazardous only", "Non-hazardous only"]
    )

    # ----------- Run filter only on button click -----------
    if st.button("Filter"):
        sql = f"""
            SELECT
                a.asteroid_id,
                a.name,
                a.absolute_magnitude_h,
                a.estimated_diameter_min_km,
                a.estimated_diameter_max_km,
                a.is_potentially_hazardous_asteroid,
                c.close_approach_date,
                c.relative_velocity_kmph,
                c.astronomical,
                c.miss_distance_km,
                c.miss_distance_lunar
            FROM asteroids a
            JOIN close_approach c
              ON a.asteroid_id = c.asteroid_id
            WHERE c.close_approach_date BETWEEN '{start_date}' AND '{end_date}'
              AND c.relative_velocity_kmph BETWEEN {vel_min} AND {vel_max}
              AND a.estimated_diameter_min_km >= {dia_min}
              AND a.estimated_diameter_max_km <= {dia_max}
              AND c.astronomical BETWEEN {au_min} AND {au_max}
              AND c.miss_distance_lunar BETWEEN {ld_min} AND {ld_max}
        """

        if hazard_option == "Hazardous only":
            sql += " AND a.is_potentially_hazardous_asteroid = 1"
        elif hazard_option == "Non-hazardous only":
            sql += " AND a.is_potentially_hazardous_asteroid = 0"

        sql += " ORDER BY c.close_approach_date ASC;"

        df = run_query(sql)

        if df.empty:
            st.warning("No asteroids match your filter criteria.")
        else:
            st.subheader("Filtered Asteroids")
            st.dataframe(df)
