import streamlit as st
import sqlite3
import pandas as pd

df = pd.read_csv(r'D:/police/traffic_stops - traffic_stops_with_vehicle_number.csv')
df.isnull().sum()
df.fillna({'search_type':'unknown'},inplace=True)


def load_data():
    return df
def fetch_data(query):
    try:
        df = load_data()
        conn = sqlite3.connect(":memory:")
        df.to_sql("traffic_stops_data", conn, index=False, if_exists="replace")
        result = pd.read_sql_query(query, conn)
        conn.close()
        return result
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return pd.DataFrame()
# Function to connect to SQLite database
def get_data(query, params=None):
    conn = sqlite3.connect("traffic_stops_project")
    if params:
        df = pd.read_sql_query(query, conn, params=params)
    else:
        df = pd.read_sql_query(query, conn)
    conn.close()
    return df


import mysql.connector
conn_mysql = mysql.connector.connect(
    host="localhost",
    user="root",
    password="abc123"
)
cursor_mysql = conn_mysql.cursor()
print("MySQL connection established!")


st.set_page_config(page_title="SecureCheck", layout="wide")
st.sidebar.title("Secure")
page = st.sidebar.radio("Go to", ["Project Introduction", "Traffic Violation Visualization", "SQL Queries"])
if page == "Project Introduction":
    st.title("SecureCheck: A Python - SQL Digital Ledger for Police Post Logs")
    st.subheader("📊 A Streamlit App for Displaying traffic voilation")
    st.write("""
    This project is to analyzes  build an SQL-based check post database with a
    Python-powered dashboard for real-time insights and alerts.
    """)
    st.markdown("""
                ### Features:
                - Real-time logging of vehicles and personnel.
                - Automated suspect vehicle identification using SQL queries.
                - Check post efficiency monitoring through data analytics.
                - Crime pattern analysis with Python scripts.
                - Centralized database for multi-location check posts.
                """)
    st.write("""
    **Database Used:** `traffic_stop_project`
    """)
elif page == "Traffic Violation Visualization":
    st.header("Traffic Violation Visualization")
    
    # --- User Form ---
    with st.form("new_log_form"):
        stop_date = st.date_input("Stop Date")
        stop_time = st.time_input("Stop Time")
        county_name = st.text_input("County Name")
        driver_gender = st.selectbox("Driver Gender", ["male", "female"])
        driver_age = st.number_input("Driver Age", min_value=16, max_value=100, value=27)
        driver_race = st.text_input("Driver Race")
        search_conducted = st.selectbox("Was a Search Conducted?", ["0", "1"])
        search_type = st.text_input("Search Type")
        drugs_related_stop = st.selectbox("Was it Drug Related?", ["0", "1"])
        stop_duration = st.selectbox("stop Duration", df['stop_duration'].dropna().unique())
        vehicle_number = st.text_input("vehicle Number")
        timestamp = pd.Timestamp.now()
        submitted = st.form_submit_button("Predict Stop Outcome & Violation")
    # --- When the user submits the form ---
    if submitted:
        # ✅ Filter the data based on user inputs
        filtered_data = df[
            (df['driver_gender'] == driver_gender) &
            (df['driver_age'] == driver_age) &
            (df['search_conducted'] == int(search_conducted)) &
            (df['stop_duration'] == stop_duration) &
            (df['drugs_related_stop'] == int(drugs_related_stop))
        ]

        # ✅ Check if we have matching data
        if not filtered_data.empty:
            predicted_outcome = filtered_data['stop_outcome'].mode()[0]
            predicted_violation = filtered_data['violation'].mode()[0]
        else:
            predicted_outcome = "Warning"    # Default fallback
            predicted_violation = "Speeding"  # Default fallback

        # ✅ Human-readable text
        search_text = "A search was conducted" if int(search_conducted) else "No search was conducted"
        drug_text = "was drug-related" if int(drugs_related_stop) else "was not drug-related"

        # ✅ Display result summary
        st.markdown(f"""
        ### 🔍 Prediction Summary
        - **Predicted Violation:** {predicted_violation}
        - **Predicted Stop Outcome:** {predicted_outcome}

        A {driver_age}-year-old **{driver_gender}** driver in **{county_name}**  
        was stopped at **{stop_time.strftime('%I:%M %p')}** on **{stop_date}**.  
        {search_text}, and the stop {drug_text}.  
        Stop Duration: **{stop_duration}**  
        Vehicle Number: **{vehicle_number}**
        """)

elif page == "SQL Queries": 
    st.title("Advanced Insights")

    selected_query = st.selectbox("Select a Query to Run", [
        "The top 10 vehicle_Number involved in drug-related stops",
        "Vehicles were most frequently searched",
        "Driver age group had the highest arrest rate",
        "The gender distribution of drivers stopped in each country",
        "Race and gender combination has the highest search rate",
        "Time of day sees the most traffic stops",
        "The average stop duration for different violations",
        "Stops during the night more likely to lead to arrests",
        "Violations are most associated with searches or arrests",
        "Violations are most common among younger drivers (<25)",
        "There is a violation that rarely results in search or arrest",
        "Countries report the highest rate of drug-related stops",
        "The arrest rate by country and violation",
        "Country has the most stops with search conducted",
        "Yearly Breakdown of Stops and Arrests by Country ",
        "Driver Violation Trends Based on Age and Race",
        "Time Period Analysis of Stops ,Number of Stops by Year,Month, Hour of the Day",
        "Violations with High Search and Arrest Rates",
        "Driver Demographics by Country ",
        "Top 5 Violations with Highest Arrest Rates"
    ])
    query_map = {
    "The top 10 vehicle_Number involved in drug-related stops":
        "select vehicle_Number from traffic_stops_data where ( drugs_related_stop=True ) limit 10",

    "Vehicles were most frequently searched": """
        SELECT 
            vehicle_number, COUNT(*) AS search_count
        FROM 
            traffic_stops_data
        GROUP BY 
            vehicle_number
        ORDER BY 
            search_count DESC
        LIMIT 1;
    """,

    "Driver age group had the highest arrest rate":
        "select driver_age,count(*) as total from traffic_stops_data where is_arrested = True group by driver_age ORDER BY total DESC limit 1",

    "The gender distribution of drivers stopped in each country": """
        SELECT 
            country_name,
            driver_gender,
            COUNT(*) AS total_stops
        FROM 
            traffic_stops_data
        GROUP BY 
            country_name, driver_gender
        ORDER BY 
            country_name, total_stops DESC;
    """,

    "Race and gender combination has the highest search rate": """
        SELECT 
            driver_race, 
            driver_gender, 
            COUNT(*) AS Count1
        FROM 
            traffic_stops_data
        WHERE 
            search_conducted = TRUE
        GROUP BY 
            driver_race, driver_gender
        ORDER BY 
            Count1 DESC 
        LIMIT 1;
    """,
    "Time of day sees the most traffic stops":"""
        WITH RECURSIVE hours(hour) AS (
    SELECT 0
    UNION ALL
    SELECT hour + 1 FROM hours WHERE hour < 23
)
SELECT
    h.hour AS hour_of_day,
    COUNT(t.stop_time) AS total_stops
FROM hours h
LEFT JOIN traffic_stops_data t
    ON CAST(strftime('%H', t.stop_time) AS INTEGER) = h.hour
GROUP BY h.hour
ORDER BY h.hour;

    """,

    "The average stop duration for different violations": """
        SELECT 
            violation,
            AVG(stop_duration) AS avg_stop_duration,
            COUNT(*) AS total_stops
        FROM 
            traffic_stops_data
        GROUP BY 
            violation
        ORDER BY 
            avg_stop_duration DESC;
    """,

    "Stops during the night more likely to lead to arrests": """
        SELECT
    CASE
        WHEN CAST(strftime('%H', stop_time) AS INTEGER) BETWEEN 20 AND 23 THEN 'Night'
        WHEN CAST(strftime('%H', stop_time) AS INTEGER) BETWEEN 0 AND 4 THEN 'Late Night'
        ELSE 'Daytime'
    END AS time_period,
    COUNT(*) AS total_stops,
    SUM(is_arrested) AS arrests,
    ROUND(100.0 * SUM(is_arrested) / COUNT(*), 2) AS arrest_rate_percent
    FROM traffic_stops_data
    GROUP BY time_period
    ORDER BY arrest_rate_percent DESC;

    """,

    "Violations are most associated with searches or arrests": """
        SELECT 
            violation, COUNT(*) AS hg
        FROM 
            traffic_stops_data
        WHERE
            search_conducted = TRUE OR is_arrested = TRUE
        GROUP BY 
            violation
        ORDER BY 
            hg DESC 
        LIMIT 3;
    """,

    "Violations are most common among younger drivers (<25)": """
        SELECT 
            violation, COUNT(*) AS aba
        FROM 
            traffic_stops_data
        WHERE 
            driver_age < 25
        GROUP BY 
            violation
        ORDER BY 
            aba DESC 
        LIMIT 1;
    """,

    "There is a violation that rarely results in search or arrest": """
        SELECT
        violation,
        COUNT(*) AS total_stops,
        SUM(search_conducted) AS total_searches,
        SUM(is_arrested) AS total_arrests,
        ROUND(
            100.0 * (SUM(search_conducted) + SUM(is_arrested)) / COUNT(*),
            2
        ) AS search_or_arrest_rate
        FROM traffic_stops_data
        GROUP BY violation
        ORDER BY search_or_arrest_rate ASC
        LIMIT 3;


    """,

    "Countries report the highest rate of drug-related stops": """
        SELECT 
            country_name, COUNT(*) AS ds
        FROM 
            traffic_stops_data
        WHERE 
            drugs_related_stop = TRUE
        GROUP BY 
            country_name
        ORDER BY 
            ds DESC 
        LIMIT 5;
    """,

    "The arrest rate by country and violation": """
        SELECT
    country_name,
    violation,
    SUM(is_arrested) AS arrest_count,
    COUNT(*) AS total_count,
    ROUND(100.0 * SUM(is_arrested) / COUNT(*), 2) AS arrest_rate_percent
    FROM
        traffic_stops_data
    GROUP BY
        country_name, violation
    ORDER BY
        arrest_rate_percent DESC
    LIMIT 5;

    """,

    "Country has the most stops with search conducted": """
        SELECT 
            country_name, COUNT(*) AS df
        FROM 
            traffic_stops_data
        WHERE 
            search_conducted = TRUE
        GROUP BY 
            country_name
        ORDER BY 
            df
        LIMIT 1;
    """,

    "Yearly Breakdown of Stops and Arrests by Country ": """
        SELECT
    country_name,
    strftime('%Y', stop_date) AS year,
    COUNT(*) AS total_stops,
    SUM(is_arrested) AS total_arrests
    FROM traffic_stops_data
    GROUP BY country_name, year
    ORDER BY country_name, year;

    """,

    "Driver Violation Trends Based on Age and Race": """
        SELECT 
            v.driver_age_group,
            v.driver_race,
            v.violation,
            COUNT(*) AS total_violations
        FROM (
            SELECT 
                driver_age,
                driver_race,
                violation,
                CASE 
                    WHEN driver_age < 25 THEN 'Under 25'
                    WHEN driver_age BETWEEN 25 AND 40 THEN '25-40'
                    WHEN driver_age BETWEEN 41 AND 60 THEN '41-60'
                    ELSE '60+'
                END AS driver_age_group
            FROM traffic_stops_data
        ) AS v
        GROUP BY 
            v.driver_age_group, v.driver_race, v.violation
        ORDER BY 
            v.driver_age_group, v.driver_race, total_violations DESC;
    """,

    "Time Period Analysis of Stops ,Number of Stops by Year,Month, Hour of the Day": """
        SELECT
    strftime('%Y', stop_date) AS year,
    strftime('%m', stop_date) AS month,
    strftime('%H', stop_time) AS hour,
    COUNT(*) AS total_stops
    FROM traffic_stops_data
    GROUP BY year, month, hour
    ORDER BY year, month, hour;

    """,

    "Violations with High Search and Arrest Rates": """
        SELECT 
            violation,
            COUNT(*) AS total_stops,
            SUM(search_conducted) AS total_searches,
            SUM(is_arrested) AS total_arrests,
            ROUND(100 * SUM(search_conducted) / COUNT(*), 2) AS search_rate,
            ROUND(100 * SUM(is_arrested) / COUNT(*), 2) AS arrest_rate,
            RANK() OVER (ORDER BY ROUND(100 * SUM(is_arrested) / COUNT(*), 2) DESC) AS arrest_rank
        FROM 
            traffic_stops_data
        GROUP BY 
            violation
        ORDER BY 
            arrest_rate DESC
        LIMIT 10;
    """,

    "Driver Demographics by Country ": """
        SELECT 
            country_name,
            ROUND(AVG(driver_age), 1) AS avg_age,
            COUNT(DISTINCT driver_gender) AS gender_diversity,
            COUNT(DISTINCT driver_race) AS race_diversity,
            COUNT(*) AS total_drivers
        FROM 
            traffic_stops_data
        GROUP BY 
            country_name
        ORDER BY 
            total_drivers DESC;
    """,

    "Top 5 Violations with Highest Arrest Rates": """
        SELECT 
            violation,
            COUNT(*) AS total_stops,
            SUM(is_arrested) AS total_arrests,
            ROUND(100 * SUM(is_arrested) / COUNT(*), 2) AS arrest_rate
        FROM 
            traffic_stops_data
        GROUP BY 
            violation
        ORDER BY 
            arrest_rate DESC
        LIMIT 5;
    """

}
    if st.button("Run Query"):
        result = fetch_data(query_map[selected_query])
        if not result.empty:
            st.write(result)
        else:
            st.warning("No results found for the selected query.")
cursor_mysql.execute("CREATE DATABASE IF NOT EXISTS traffic_stops_project;")
print("MySQL database 'traffic_stop_project' created successfully!")
cursor_mysql.execute("USE traffic_stops_project;")  
cursor_mysql.execute("""
    CREATE TABLE IF NOT EXISTS traffic_stops_data (
       stop_date DATE,
       stop_time TIME,
       country_name VARCHAR(50),
       driver_gender VARCHAR(50),
       driver_age_raw INT,
       driver_age INT,
       driver_race VARCHAR(50),
       violation_raw VARCHAR(50),
       violation VARCHAR(50),
       search_conducted BOOLEAN,
       search_type VARCHAR(50),
       stop_outcome VARCHAR(50),
       is_arrested BOOLEAN,
       stop_duration VARCHAR(50),
       drugs_related_stop BOOL,
       vehicle_number VARCHAR(50)
    );
""")
conn_mysql.commit()
print("Table 'traffic_stops_data' created successfully in MySQL!")


data_list = df.values.tolist()
query = """
    INSERT INTO traffic_stops_data ( stop_date,stop_time,country_name,driver_gender,driver_age_raw,driver_age,driver_race,violation_raw,violation,search_conducted,search_type,stop_outcome,is_arrested,stop_duration,drugs_related_stop,vehicle_number)
    VALUES (%s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""
cursor_mysql.executemany(query, data_list)
conn_mysql.commit()
print("Data inserted using to_list()")


Query1="""
SELECT vehicle_number
FROM traffic_stops_data
WHERE drugs_related_stop = TRUE
LIMIT 10;
"""
Query2="""
SELECT vehicle_number, COUNT(*) AS search_count
FROM traffic_stops_data
GROUP BY vehicle_number
ORDER BY search_count DESC
LIMIT 1;
"""
Query3="""
SELECT driver_age, COUNT(*) AS total
FROM traffic_stops_data
WHERE is_arrested = TRUE
GROUP BY driver_age
ORDER BY total DESC
LIMIT 1;
"""

Query4="""
SELECT country_name, driver_gender, COUNT(*) AS total_stops
FROM traffic_stops_data
GROUP BY country_name, driver_gender
ORDER BY country_name, total_stops DESC;
"""

Query5="""
SELECT driver_race, driver_gender, COUNT(*) AS Count1
FROM traffic_stops_data
WHERE search_conducted = TRUE
GROUP BY driver_race, driver_gender
ORDER BY Count1 DESC
LIMIT 1;
"""

Query6="""
SELECT 
    HOUR(stop_time) AS hour_of_day,
    COUNT(*) AS stop_count
FROM 
    traffic_stops_data
GROUP BY 
    HOUR(stop_time)
ORDER BY 
    stop_count DESC
LIMIT 1;
"""

Query7="""
SELECT violation, COUNT(*) AS total_stops
FROM traffic_stops_data
GROUP BY violation
ORDER BY total_stops DESC;
"""

Query8="""  
SELECT 
    CASE 
        WHEN HOUR(stop_time) BETWEEN 20 AND 23 THEN 'Night'
        WHEN HOUR(stop_time) BETWEEN 0 AND 4 THEN 'Late Night'
        ELSE 'Daytime'
    END AS time_period,
    COUNT(*) AS total_stops,
    SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS arrests,
    ROUND(SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS arrest_rate_percent
FROM 
    traffic_stops_data
GROUP BY 
    time_period
ORDER BY 
    arrest_rate_percent DESC;
"""

Query9="""
SELECT violation, COUNT(*) AS hg
FROM traffic_stops_data
WHERE search_conducted = TRUE OR is_arrested = TRUE
GROUP BY violation
ORDER BY hg DESC
LIMIT 3;
"""

Query10="""
SELECT violation, COUNT(*) AS aba
FROM traffic_stops_data
WHERE driver_age < 25
GROUP BY violation
ORDER BY aba DESC
LIMIT 1;
"""

Query11="""

SELECT violation,
       COUNT(*) AS total_stops,
       SUM(search_conducted) AS total_searches,
       SUM(is_arrested) AS total_arrests,
       ROUND(100.0 * (SUM(search_conducted) + SUM(is_arrested)) / COUNT(*), 2) AS search_or_arrest_rate
FROM traffic_stops_data
GROUP BY violation
ORDER BY search_or_arrest_rate ASC
LIMIT 3;
"""

Query12="""
SELECT country_name, COUNT(*) AS ds
FROM traffic_stops_data
WHERE drugs_related_stop = TRUE
GROUP BY country_name
ORDER BY ds DESC
LIMIT 5;
"""

Query13="""
SELECT country_name, violation,
       SUM(is_arrested) AS arrest_count,
       COUNT(*) AS total_count,
       ROUND(100.0 * SUM(is_arrested) / COUNT(*), 2) AS arrest_rate_percent
FROM traffic_stops_data
GROUP BY country_name, violation
ORDER BY arrest_rate_percent DESC
LIMIT 5;
"""

Query14="""
SELECT country_name, COUNT(*) AS df
FROM traffic_stops_data
WHERE search_conducted = TRUE
GROUP BY country_name
ORDER BY df DESC
LIMIT 1;
"""

Query15="""
SELECT country_name,
       strftime('%Y', stop_date) AS year,
       COUNT(*) AS total_stops,
       SUM(is_arrested) AS total_arrests
FROM traffic_stops_data
GROUP BY country_name, year
ORDER BY country_name, year;
"""

Query16="""
SELECT 
    v.driver_age_group,
    v.driver_race,
    v.violation,
    COUNT(*) AS total_violations
FROM (
    SELECT 
        driver_age,
        driver_race,
        violation,
        CASE 
            WHEN driver_age < 25 THEN 'Under 25'
            WHEN driver_age BETWEEN 25 AND 40 THEN '25-40'
            WHEN driver_age BETWEEN 41 AND 60 THEN '41-60'
            ELSE '60+'
        END AS driver_age_group
    FROM traffic_stops_data
) AS v
GROUP BY 
    v.driver_age_group, v.driver_race, v.violation
ORDER BY 
    v.driver_age_group, v.driver_race, total_violations DESC;
"""

Query17="""
SELECT strftime('%Y', stop_date),
       strftime('%m', stop_date),
       strftime('%H', stop_time),
       COUNT(*)
FROM traffic_stops_data
GROUP BY year, month, hour;
"""

Query18="""
SELECT 
    violation,
    COUNT(*) AS total_stops,
    SUM(search_conducted) AS total_searches,
    SUM(is_arrested) AS total_arrests,
    ROUND(100 * SUM(search_conducted) / COUNT(*), 2) AS search_rate,
    ROUND(100 * SUM(is_arrested) / COUNT(*), 2) AS arrest_rate,
    RANK() OVER (ORDER BY ROUND(100 * SUM(is_arrested) / COUNT(*), 2) DESC) AS arrest_rank
FROM 
    traffic_stops_data
GROUP BY 
    violation
ORDER BY 
    arrest_rate DESC
LIMIT 10;
"""

Query19="""
SELECT country_name,
       AVG(driver_age),
       COUNT(DISTINCT driver_gender),
       COUNT(DISTINCT driver_race)
FROM traffic_stops_data
GROUP BY country_name;
"""

Query20="""
SELECT violation,
       COUNT(*),
       SUM(is_arrested),
       ROUND(100 * SUM(is_arrested) / COUNT(*), 2)
FROM traffic_stops_data
GROUP BY violation
ORDER BY arrest_rate DESC
LIMIT 5;
"""