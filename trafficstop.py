
import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
df = pd.read_csv(r'D:/police/traffic_stops - traffic_stops_with_vehicle_number.csv')
df.isnull().sum()
df.fillna({'search_type':'unknown'},inplace=True)
import mysql.connector
conn_mysql = mysql.connector.connect(
    host="localhost",
    user="root",
    password="abc123"
)
cursor_mysql = conn_mysql.cursor()
print("MySQL connection established!")

def load_data():
    return df
def fetch_data(query):
    try:
        df = load_data()
        conn = sqlite3.connect(":memory:")
        df.to_sql("police_data", conn, index=False, if_exists="replace")
        result = pd.read_sql_query(query, conn)
        conn.close()
        return result
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return pd.DataFrame()
# Function to connect to SQLite database
def get_data(query, params=None):
    conn = sqlite3.connect("police_db_data")
    if params:
        df = pd.read_sql_query(query, conn, params=params)
    else:
        df = pd.read_sql_query(query, conn)
    conn.close()
    return df
st.set_page_config(page_title="SecureCheck", layout="wide")
st.sidebar.title("Secure")
page = st.sidebar.radio("Go to", ["Project Introduction", "Traffic Violation Visualation ", "SQL Queries"])
if page == "Project Introduction":
    st.title("police:SecureCheck")
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
    **Database Used:** `police_db_data`
""")

elif page == "Traffic Violation Visualization":
    st.title("🚦 Traffic Violation Visualization")

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

        # ✅ use CSV column for dropdown
        stop_duration = st.selectbox(
            "Stop Duration", 
            df['stop_duration'].dropna().unique()
        )

        vehicle_number = st.text_input("Vehicle Number")
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
    st.header("Advanced Insights")
    selected_query = st.selectbox("Select a Query to Run", [
        "The top 10 vehicle_Number involved in drug-related stops",
        "Vehicles were most frequently searched",
        "Driver age group had the highest arrest rate",
        "The gender distribution of drivers stopped in each country",
        "Race and gender combination has the highest search rate",
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
            "SELECT vehicle_Number FROM police_data WHERE drugs_related_stop = TRUE LIMIT 10;",

        "Vehicles were most frequently searched": """
            SELECT 
                vehicle_number, COUNT(*) AS search_count
            FROM 
                police_data
            GROUP BY 
                vehicle_number
            ORDER BY 
                search_count DESC
            LIMIT 1;
        """,

        "Driver age group had the highest arrest rate":
            "SELECT driver_age, COUNT(*) AS total FROM police_data WHERE is_arrested = TRUE GROUP BY driver_age ORDER BY total DESC LIMIT 1;",

        "The gender distribution of drivers stopped in each country": """
            SELECT 
                country_name,
                driver_gender,
                COUNT(*) AS total_stops
            FROM 
                police_data
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
                police_data
            WHERE 
                search_conducted = TRUE
            GROUP BY 
                driver_race, driver_gender
            ORDER BY 
                Count1 DESC 
            LIMIT 1;
        """,

        "The average stop duration for different violations": """
            SELECT 
                violation,
                AVG(stop_duration) AS avg_stop_duration,
                COUNT(*) AS total_stops
            FROM 
                police_data
            GROUP BY 
                violation
            ORDER BY 
                avg_stop_duration DESC;
        """,

        "Stops during the night more likely to lead to arrests": """
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
                police_data
            GROUP BY 
                time_period
            ORDER BY 
                arrest_rate_percent DESC;
        """,

        "Violations are most associated with searches or arrests": """
            SELECT 
                violation, COUNT(*) AS hg
            FROM 
                police_data
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
                police_data
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
                violation, COUNT(*) AS aba
            FROM 
                police_data
            WHERE  
                (search_conducted = TRUE OR is_arrested = TRUE) 
            GROUP BY 
                violation
            HAVING 
                aba < 10
            ORDER BY 
                aba  
            LIMIT 1;
        """,

        "Countries report the highest rate of drug-related stops": """
            SELECT 
                country_name, COUNT(*) AS ds
            FROM 
                police_data
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
                SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS arrest_count,
                COUNT(*) AS total_count,
                ROUND(SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS arrest_rate_percent
            FROM 
                police_data
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
                police_data
            WHERE 
                search_conducted = TRUE
            GROUP BY 
                country_name
            ORDER BY 
                df DESC
            LIMIT 1;
        """,

        "Yearly Breakdown of Stops and Arrests by Country ": """
            SELECT 
                country_name,
                year,
                COUNT(*) AS total_stops,
                SUM(is_arrested) AS total_arrests,
                SUM(SUM(is_arrested)) OVER (PARTITION BY country_name ORDER BY year) AS cumulative_arrests
            FROM (
                SELECT 
                    country_name,
                    YEAR(stop_time) AS year,
                    is_arrested
                FROM police_data
            ) AS sub
            GROUP BY 
                country_name, year
            ORDER BY 
                country_name, year;
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
                FROM police_data
            ) AS v
            GROUP BY 
                v.driver_age_group, v.driver_race, v.violation
            ORDER BY 
                v.driver_age_group, v.driver_race, total_violations DESC;
        """,

        "Time Period Analysis of Stops ,Number of Stops by Year,Month, Hour of the Day": """
            SELECT 
                t.year,
                t.month,
                t.hour,
                COUNT(*) AS total_stops
            FROM (
                SELECT
                    YEAR(stop_time) AS year,
                    MONTH(stop_time) AS month,
                    HOUR(stop_time) AS hour
                FROM police_data
            ) AS t
            GROUP BY 
                t.year, t.month, t.hour
            ORDER BY 
                t.year, t.month, t.hour;
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
                police_data
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
                police_data
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
                police_data
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

cursor_mysql.execute("CREATE DATABASE IF NOT EXISTS police_db_data;")
print("MySQL database 'police_db_data' created successfully!")
cursor_mysql.execute("USE police_db_data;")  # Select database
cursor_mysql.execute("""
    CREATE TABLE IF NOT EXISTS police_data (
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
print("Table 'police_data' created successfully in MySQL!")

data_list = df.values.tolist()
query = """
    INSERT INTO police_data ( stop_date,stop_time,country_name,driver_gender,driver_age_raw,driver_age,driver_race,violation_raw,violation,search_conducted,search_type,stop_outcome,is_arrested,stop_duration,drugs_related_stop,vehicle_number)
    VALUES (%s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""
cursor_mysql.executemany(query, data_list)
conn_mysql.commit()
print("Data inserted")

#1What are the top 10 vehicle_Number involved in drug-related stops?
from tabulate import tabulate
query1="select vehicle_Number from police_data where ( drugs_related_stop=True ) limit 10"
cursor_mysql.execute(query1)
records =cursor_mysql.fetchall() # Fetches the first 10 rows
headers = ["vehicle_number"]
print("1.What are the top 10 vehicle_Number involved in drug-related stops?")
print(tabulate(records, headers=headers, tablefmt="grid"))
#2Which vehicles were most frequently searched
query2="""SELECT vehicle_number, COUNT(*) AS search_count FROM police_data GROUP BY vehicle_number ORDER BY search_count DESC
LIMIT 1;
"""
cursor_mysql.execute(query2)
records1 =cursor_mysql.fetchall()
headers = ["vehicle_number","search_count"]
print("2.Which vehicles were most frequently searched?")
print(tabulate(records1, headers=headers, tablefmt="grid"))
#Which driver age group had the highest arrest rate
from tabulate import tabulate
query3="select driver_age,count(*) as total from police_data where is_arrested = True group by driver_age ORDER BY total  DESC limit 1"
cursor_mysql.execute(query3)
records2 =cursor_mysql.fetchall()
headers = ["driver_age","total"]
print("4.Which driver age group had the highest arrest rate?")
print(tabulate(records2, headers=headers, tablefmt="grid"))
#What is the gender distribution of drivers stopped in each country
query4="""
SELECT 
    country_name,
    driver_gender,
    COUNT(*) AS total_stops
FROM 
    police_data
GROUP BY 
    country_name, driver_gender
ORDER BY 
    country_name, total_stops DESC;
"""
cursor_mysql.execute(query4)

records3 =cursor_mysql.fetchall()
headers = ["Country_name","driver_gender","total_stops"]
print("5.What is the gender distribution of drivers stopped in each country?")
print(tabulate(records3, headers=headers, tablefmt="grid"))

#Which race and gender combination has the highest search rate?
query5 = """
SELECT
    driver_race,
    driver_gender,
    SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) AS total_searches,
    ROUND(
        (SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) / COUNT(*)) * 100,
        2
    ) AS search_rate_percentage
FROM
    police_data
GROUP BY
    driver_race, driver_gender
ORDER BY
    search_rate_percentage DESC
LIMIT 1;
"""
cursor_mysql.execute(query5)
records4 = cursor_mysql.fetchall()
headers = ["driver_race","driver_gender","total_searches","search_rate_percentage"]
print("6.Which race and gender combination has the highest search rate?")
print(tabulate(records4, headers=headers, tablefmt="grid"))
#7.What time of day sees the most traffic stops  
query6 = """SELECT stop_time, COUNT(*) AS total_stops FROM police_data GROUP BY stop_time ORDER BY total_stops DESC
LIMIT 1;
"""
cursor_mysql.execute(query6)
records5 = cursor_mysql.fetchall()
headers = ["Stop Time","total_stops"]
print("7.What time of day sees the most traffic stops")
print(tabulate(records5, headers=headers, tablefmt="grid"))
#8.What is the average stop duration for different violations?
query8 = """
SELECT 
    violation,
    AVG(stop_duration) AS avg_stop_duration,
    COUNT(*) AS total_stops
FROM 
    police_data
GROUP BY 
    violation
ORDER BY 
    avg_stop_duration DESC;
"""
cursor_mysql.execute(query8)
records6 = cursor_mysql.fetchall()
headers = ["violation","avg_stop_duration","total_stops"]
print("8.What is the average stop duration for different violations?")
print(tabulate(records6, headers=headers, tablefmt="grid"))
#9.Are stops during the night more likely to lead to arrests?
query9="""   
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
    police_data
GROUP BY 
    time_period
ORDER BY 
    arrest_rate_percent DESC;
"""
cursor_mysql.execute(query9)
records7 = cursor_mysql.fetchall()
headers = ["time_period","total_stops","arrests","arrest_rate_percent"]
print("9.Are stops during the night more likely to lead to arrests?")
print(tabulate(records7, headers=headers, tablefmt="grid"))
for row in records2:
        print(row)
#10.Which violations are most associated with searches or arrests?
query10="""
select 
    violation,count(*)as hg
from 
    police_data
where
    search_conducted=true or is_arrested=true
group by 
    violation
order by
    hg desc 
limit 3
"""
cursor_mysql.execute(query10)
records8 = cursor_mysql.fetchall()
headers = ["Violation","HG"]
print("10.Which violations are most associated with searches or arrests?")
print(tabulate(records8, headers=headers, tablefmt="grid"))

#11.Which violations are most common among younger drivers (<25)
query11="""
select 
    violation,count(*) as aba
from 
    police_data
where 
    driver_age < 25
group by 
    violation
order by
    aba desc limit 1;
"""
cursor_mysql.execute(query11)
records9 = cursor_mysql.fetchall()
headers = ["Violation","ABA"]
print("11.Which violations are most common among younger drivers (<25)?")
print(tabulate(records9, headers=headers, tablefmt="grid"))


#Is there a violation that rarely results in search or arrest
query12="""
select 
    violation,count(*) as aba
from 
    police_data
where  
    (search_conducted=true or is_arrested=true) 
group by 
    violation
having
    aba <10
order by
    aba  limit 1;
"""
cursor_mysql.execute(query12)
records10 = cursor_mysql.fetchall()
print("12.Is there a violation that rarely results in search or arrest?")

if not records10:
   print('NO') 
else :print(records10)

#Which countries report the highest rate of drug-related stops
query13="""
select 
    country_name,count(*) as ds
from 
    police_data
where 
    drugs_related_stop=true
group by
     country_name
order by 
     ds desc limit 5
"""
cursor_mysql.execute(query13)
records11 = cursor_mysql.fetchall()
headers = ["COUNTRY NAME","DS"]
print("13.Which countries report the highest rate of drug-related stops?")
print(tabulate(records11, headers=headers, tablefmt="grid"))

#What is the arrest rate by country and violation
query14="""
SELECT 
    country_name,
    violation,
    SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS arrest_count,
    COUNT(*) AS total_count,
    ROUND(SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS arrest_rate_percent
FROM 
    police_data
GROUP BY 
    country_name, violation
ORDER BY 
    arrest_rate_percent DESC
LIMIT 5;

"""
cursor_mysql.execute(query14)
records12 = cursor_mysql.fetchall()
headers = ["COUNTRY NAME","VIOLATION","ARREST COUNT","TOTAL ARREST","ARREST RATE PERCENTAGE"]
print("14.What is the arrest rate by country and violation?")
print(tabulate(records12, headers=headers, tablefmt="grid"))

#Which country has the most stops with search conducted
query15="""
SELECT 
    country_name,count(*) as df
FROM 
    police_data
where 
    search_conducted=true
GROUP BY 
    country_name
ORDER BY 
    df
LIMIT 1;
"""
cursor_mysql.execute(query15)
records13 = cursor_mysql.fetchall()
headers = ["COUNTRY NAME","DF"]
print("15.Which country has the most stops with search conducted")
print(tabulate(records13, headers=headers, tablefmt="grid"))

query_yearly_breakdown = """
SELECT
    country_name,
    YEAR(stop_date) AS year,
    COUNT(*) AS total_stops,
    SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS total_arrests,
    ROUND(
        (SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) / COUNT(*)) * 100,
        2
    ) AS arrest_rate_percentage,
    RANK() OVER (PARTITION BY country_name ORDER BY YEAR(stop_date)) AS year_rank
FROM
    police_data
GROUP BY
    country_name, YEAR(stop_date)
ORDER BY
    country_name, year;
"""
cursor_mysql.execute(query_yearly_breakdown)
yearly_breakdown_results = cursor_mysql.fetchall()
headers = ["Country", "Year", "Total Stops", "Total Arrests", "Arrest Rate (%)", "Year Rank"]
print("1.Yearly Breakdown of Stops and Arrests by Country:")
print(tabulate(yearly_breakdown_results, headers=headers, tablefmt="grid"))


query_violation_trends = """
SELECT
    v.driver_race,
    v.driver_age,
    v.violation,
    COUNT(*) AS total_stops,
    ROUND(
        (COUNT(*) / (SELECT COUNT(*) FROM police_data)) * 100,
        2
    ) AS percentage_of_total
FROM
    police_data v
JOIN (
    SELECT driver_race, driver_age
    FROM police_data
    WHERE driver_age IS NOT NULL
) sub ON v.driver_race = sub.driver_race AND v.driver_age = sub.driver_age
GROUP BY
    v.driver_race, v.driver_age, v.violation
ORDER BY
    v.driver_race, v.driver_age, total_stops DESC
LIMIT 20;
"""
cursor_mysql.execute(query_violation_trends)
violation_trends_results = cursor_mysql.fetchall()
headers = ["Race", "Age", "Violation", "Total Stops", "% of Total"]
print("2.Driver Violation Trends Based on Age and Race:")
print(tabulate(violation_trends_results, headers=headers, tablefmt="grid"))



query_time_analysis = """
SELECT
    YEAR(stop_date) AS year,
    MONTH(stop_date) AS month,
    HOUR(stop_time) AS hour_of_day,
    COUNT(*) AS total_stops
FROM
    police_data
GROUP BY
    YEAR(stop_date), MONTH(stop_date), HOUR(stop_time)
ORDER BY
    year, month, hour_of_day;
"""
cursor_mysql.execute(query_time_analysis)
time_analysis_results = cursor_mysql.fetchall()
headers = ["Year", "Month", "Hour of Day", "Total Stops"]
print("3.Time Period Analysis of Stops (Year, Month, Hour):")
print(tabulate(time_analysis_results, headers=headers, tablefmt="grid"))



query_high_enforcement = """
SELECT
    violation,
    COUNT(*) AS total_stops,
    SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) AS total_searches,
    SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS total_arrests,
    ROUND(
        (SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2
    ) AS search_rate,
    ROUND(
        (SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2
    ) AS arrest_rate,
    RANK() OVER (ORDER BY
        (SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) / COUNT(*)) * 100 +
        (SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) / COUNT(*)) * 100 DESC
    ) AS enforcement_rank
FROM
    police_data
GROUP BY
    violation
ORDER BY
    enforcement_rank
LIMIT 10;
"""
cursor_mysql.execute(query_high_enforcement)
high_enforcement_results = cursor_mysql.fetchall()
headers = ["Violation", "Total Stops", "Total Searches", "Total Arrests", "Search Rate (%)", "Arrest Rate (%)", "Rank"]
print("4.Violations with High Search & Arrest Rates (Ranked):")
print(tabulate(high_enforcement_results, headers=headers, tablefmt="grid"))



query_demographics = """
SELECT
    country_name,
    ROUND(AVG(driver_age), 2) AS avg_age,
    SUM(CASE WHEN driver_gender = 'M' THEN 1 ELSE 0 END) AS male_drivers,
    SUM(CASE WHEN driver_gender = 'F' THEN 1 ELSE 0 END) AS female_drivers,
    COUNT(*) AS total_drivers,
    ROUND(
        (SUM(CASE WHEN driver_gender = 'M' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2
    ) AS male_percentage,
    ROUND(
        (SUM(CASE WHEN driver_gender = 'F' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2
    ) AS female_percentage,
    (SELECT driver_race FROM police_data pr WHERE pr.country_name = pt.country_name GROUP BY driver_race ORDER BY COUNT(*) DESC LIMIT 1) AS most_common_race
FROM
    police_data pt
GROUP BY
    country_name
ORDER BY
    country_name;
"""
cursor_mysql.execute(query_demographics)
demographics_results = cursor_mysql.fetchall()
headers = ["Country", "Avg Age", "Male Drivers", "Female Drivers", "Total Drivers", "Male %", "Female %", "Most Common Race"]
print("5.Driver Demographics by Country:")
print(tabulate(demographics_results, headers=headers, tablefmt="grid"))



query_top_arrests = """
SELECT
    violation,
    COUNT(*) AS total_stops,
    SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS total_arrests,
    ROUND(
        (SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) / COUNT(*)) * 100,
        2
    ) AS arrest_rate_percentage
FROM
    police_data
GROUP BY
    violation
ORDER BY
    arrest_rate_percentage DESC
LIMIT 5;
"""
cursor_mysql.execute(query_top_arrests)
top_arrests_results = cursor_mysql.fetchall()
headers = ["Violation", "Total Stops", "Total Arrests", "Arrest Rate (%)"]
print("6.Top 5 Violations with Highest Arrest Rates:")
print(tabulate(top_arrests_results, headers=headers, tablefmt="grid"))


st.set_page_config(page_title="SecureCheck", layout="wide")
st.sidebar.title("Secure")