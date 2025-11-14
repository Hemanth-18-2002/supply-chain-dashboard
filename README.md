# Supply Chain Data Warehouse & Dashboard

This project is an end-to-end data engineering solution that builds a robust data warehouse from a single, flat data source. It uses an **ELT (Extract, Load, Transform)** process on **Google BigQuery**, converting denormalized data into a high-performance **Star Schema**.

The data model features **Slowly Changing Dimensions (SCD) Type 2** to accurately track historical changes to products, customers, and locations. The entire data warehouse serves as the backend for an interactive **Streamlit** dashboard used for business intelligence and analytics.

**Live Dashboard Demo:** [https://supply-chain-dashboard-hemanth.streamlit.app/](https://supply-chain-dashboard-hemanth.streamlit.app/)

---

## 🚀 Key Features

* **Star Schema Data Model:** Transformed a single flat table (`Supply_Chain_Data`) into a clean star schema with one fact table and five dimension tables.
* **Historical Data Tracking:** Implemented **Slowly Changing Dimensions (SCD) Type 2** on `Dim_Product`, `Dim_Customer`, and `Dim_Location` to preserve historical attribute changes.
* **Efficient ELT Pipeline:** All data transformations are handled natively within Google BigQuery using SQL for maximum efficiency and scalability.
* **Interactive Dashboard:** A live Streamlit application provides a user-friendly interface for non-technical users to explore KPIs, analyze trends, and drill down into the data.

---

## 🛠️ Technology Stack

* **Cloud Platform:** Google Cloud Platform (GCP)
* **Data Warehouse:** Google BigQuery
* **Data Modeling:** SQL
* **ETL/Orchestration:** SQL (can be orchestrated via Python, Cloud Composer, or Airflow)
* **Visualization:** Streamlit

---

## Data Model: Star Schema

The core of this project is the star schema, which separates descriptive attributes (dimensions) from numeric measurements (facts). This design is the industry standard for analytics as it simplifies queries and improves performance.

**SCD Type 2** is implemented on the core business dimensions to ensure that changes over time (e.g., a customer's `Segment` changes, a product's `Category` is redefined) are captured. This is achieved by adding `start_date`, `end_date`, and `is_current` columns to the dimension tables.

```
ER-Diagram
    Dim_Product ||--o{ Fact_Sales : "has"
    Dim_Customer ||--o{ Fact_Sales : "buys"
    Dim_Location ||--o{ Fact_Sales : "at"
    Dim_Shipping ||--o{ Fact_Sales : "via"
    Dim_Date ||--o{ Fact_Sales : "on_order_date"
    Dim_Date ||--o{ Fact_Sales : "on_ship_date"
```

    Fact_Sales {
        string order_id
        string product_key "FK"
        string customer_key "FK"
        string location_key "FK"
        string shipping_key "FK"
        string order_date_key "FK"
        string ship_date_key "FK"
        float sales
        int quantity
        float profit
        float discount
        float shipping_cost
    }

    Dim_Product {
        string product_key "PK"
        string product_id
        string product_name
        string category
        date start_date
        date end_date
        bool is_current
    }

    Dim_Customer {
        string customer_key "PK"
        string customer_id
        string customer_name
        string segment
        date start_date
        date end_date
        bool is_current
    }

    Dim_Location {
        string location_key "PK"
        string postal_code
        string city
        string state
        string region
        date start_date
        date end_date
        bool is_current
    }

    Dim_Shipping {
        string shipping_key "PK"
        string ship_mode
        string order_priority
    }

    Dim_Date {
        string date_key "PK"
        date full_date
        int month
        int year
        string month_name
    }
```
📁 Project Structure
├── Project
│   ├── 1_Bronze_layer
│   ├── 2_Silver_layer
│   ├── 3_Gold_layer
├── Datasets
|   ├── Global_Superstore.csv
|   ├── Refined_and_Cleaned_Dataset.csv
├── Presentation.pptx
├── app.py                  # Main Streamlit dashboard file
├── requirements.txt        # Python dependencies
└── README.md               # You are here
```
## ⚙️ Setup & Installation
Prerequisites
Google Cloud Project:

A GCP project with the BigQuery API enabled.

A BigQuery dataset (e.g., Dimension_Tables).

Source Data:

The source Supply_Chain_Data table must be present in your BigQuery dataset.

Python Environment:

Python 3.8+

pip install -r requirements.txt

GCP Authentication:

Authenticate your local environment to access your BigQuery project:

Bash

gcloud auth application-default login
requirements.txt
streamlit
google-cloud-bigquery
pandas
plotly

## 🚀 How to Run
1. Build the Data Warehouse (ELT Pipeline)
The SQL scripts in the /sql directory are designed to be run in a specific order to build the data warehouse.

Important: Before running, you must update the project and dataset ID (e.g., trim-plexus-396409.Dimension_Tables) in each SQL file to match your own.

Execution Order:

Create Static Dimensions:

Dim_Date

Dim_Shipping

Create SCD Type 2 Dimensions:

Dim_Product

Dim_Customer

Dim_Location

Populate Dimensions:

Run all INSERT scripts for the dimensions first. The INSERT scripts for SCD tables contain the window functions to find historical versions.

Create & Populate Fact Table (LAST):

Run the CREATE TABLE and INSERT scripts for Fact_Sales. The INSERT query for the fact table contains the correct point-in-time JOIN logic (using BETWEEN start_date AND end_date) to connect to the correct version of each dimension.

2. Run the Streamlit Dashboard
Once your BigQuery tables are populated, you can launch the dashboard.

Bash

streamlit run app.py
The application will open in your default web browser.

## 📊 Dashboard Preview
The dashboard provides a high-level overview and deep-dive capabilities.

KPI Cards: At-a-glance metrics for Total Sales, Profit, Quantity, and Average Shipping Days.

Geospatial Analysis: An interactive choropleth map shows Sales & Profit by State.

Profit & Sales Analysis: Drill-down bar charts to analyze performance by Category, Sub-Category, and Customer Segment.

Interactive Filtering: Filter the entire dashboard by Region, State, Ship Mode, and more.

<img width="1448" height="498" alt="image" src="https://github.com/user-attachments/assets/4d19d0b6-390a-4a5f-a1cb-ee60976ac17d" />
<img width="1427" height="558" alt="image" src="https://github.com/user-attachments/assets/c990f73c-f5ac-4a3a-af5f-3caa7410e7ba" />
<img width="1434" height="561" alt="image" src="https://github.com/user-attachments/assets/975adc0c-2b4f-46f4-8e49-7a216116f077" />
<img width="1476" height="568" alt="image" src="https://github.com/user-attachments/assets/f71fceb1-3aca-47f1-8e5e-c72916587c54" />
<img width="1404" height="584" alt="image" src="https://github.com/user-attachments/assets/5c7d3463-3ccd-49a9-aabd-108988a6c3a5" />
<img width="1452" height="731" alt="image" src="https://github.com/user-attachments/assets/ddb5d978-0dda-4250-8755-a6b473200ad3" />
<img width="1441" height="479" alt="image" src="https://github.com/user-attachments/assets/cdf372f3-774d-4c93-ab8f-aef0f82e70ab" />
<img width="1439" height="758" alt="image" src="https://github.com/user-attachments/assets/0a3f7be0-f4ab-4680-814d-fe8da1b2fab4" />
<img width="1446" height="620" alt="image" src="https://github.com/user-attachments/assets/d830e016-b1de-42cf-8dae-0e34c0800540" />
<img width="1448" height="594" alt="image" src="https://github.com/user-attachments/assets/3cf320b8-c295-4621-bc6a-8ff648d959bf" />


