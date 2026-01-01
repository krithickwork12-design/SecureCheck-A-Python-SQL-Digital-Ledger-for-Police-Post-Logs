#  SecureCheck – Traffic Stops Analytics System

SecureCheck is a **Python–SQL based analytics project** designed to help police check posts **log, monitor, and analyze traffic stop data** efficiently. The system replaces manual logging with a **centralized database and interactive dashboard**, enabling faster decision-making and real-time insights fileciteturn0file0.

---

##  Project Purpose

Police check posts often rely on manual or poorly structured systems to record vehicle stops, which slows down investigations and monitoring. SecureCheck solves this problem by:

* Creating a **centralized SQL database** for traffic stop records
* Using **Python for data processing and analysis**
* Providing a **Streamlit dashboard** for real-time insights and reporting fileciteturn0file0

---

##  Skills & Domain

* **Skills Used:** Python, SQL, Streamlit
* **Domain:** Law Enforcement & Public Safety
* **System Type:** Real-time Monitoring & Analytics System fileciteturn0file0

---

##  Project Workflow (Step-by-Step)

### 1️ Data Collection & Storage

* Traffic stop data is collected from a CSV dataset
* A structured **SQL schema** is designed for police stop records
* Data is stored in **SQLite (for analytics)** and **MySQL (for persistence)** fileciteturn0file0

---

### 2️ Data Processing using Python

* Remove columns with only missing values
* Handle missing data (NaN values)
* Convert date, time, and boolean fields into usable formats

Python libraries used:

* `pandas`
* `sqlite3`

---

### 3️ Database Design (SQL)

A single table is created to store traffic stop information, including:

* Stop date and time
* Driver details (age, gender, race)
* Violation details
* Search, arrest, and drug-related indicators
* Vehicle number fileciteturn0file0

---

### 4️ Streamlit Dashboard

The Streamlit application provides:

*  Traffic stop logging view
*  SQL-based search and filters
*  Analytical insights and trends
*  Rule-based prediction of violation and stop outcome

**Example Output:**

> A 27-year-old male driver was stopped for Speeding at 2:30 PM. No search was conducted, and the stop was not drug-related. The stop lasted 6–15 minutes. fileciteturn0file0

---

##  SQL Analysis Covered

The project includes **medium to complex SQL queries** such as:

###  Vehicle-Based Analysis

* Top vehicles involved in drug-related stops
* Most frequently searched vehicles

###  Demographic-Based Analysis

* Arrest rates by driver age group
* Gender distribution across countries
* Race and gender combinations with highest search rates

###  Time & Duration Analysis

* Peak hours for traffic stops
* Night vs day arrest comparison
* Stop duration trends

###  Violation-Based Analysis

* Violations most associated with searches or arrests
* Violations common among younger drivers (<25)
* Violations with high arrest rates

###  Location-Based Analysis

* Countries with highest drug-related stops
* Arrest rates by country and violation

Advanced SQL concepts used:

* `CASE WHEN`
* `GROUP BY` and `HAVING`
* Recursive CTEs
* Window functions (`RANK()`)
* Date and time extraction using `strftime()` fileciteturn0file0

---

##  Project Results

* Faster check post operations using optimized SQL queries
* Automated identification of high-risk vehicles
* Real-time reporting of traffic violations
* Improved, data-driven decision-making for law enforcement 

---

##  Technologies Used

* **Python** – Data processing & logic
* **SQL** – Data analysis & reporting
* **SQLite** – In-memory analytics
* **MySQL** – Persistent database
* **Streamlit** – Interactive dashboard

---

##  Author

**S Krithick**
Data Scientist | SQL Analyst | Python Developer

---

 *This project demonstrates real-world SQL analytics, Python processing, and dashboard development for public safety systems.*
