# Technical Progress Report: Syracuse 311 Data Pipeline
**Project Title:** Real-Time Analytics and Predictive Modeling for Syracuse CityLine  
**Academic Institution:** Syracuse University - Research  
**Reporting Period:** January 1 – January 15, 2026  
**Phase:** Ingestion & Transformation (Medallion Architecture)

## 1. Project Objective
The goal of this project is to develop a production-grade data engineering pipeline that ingests municipal service requests (311 data) from the City of Syracuse. The pipeline transforms raw, heterogeneous data into an enriched format to identify service delivery inequities and provide a foundation for future predictive machine learning models.

## 2. Architecture Overview
I have implemented a **Medallion Architecture** utilizing **Databricks Unity Catalog** and **Delta Lake**. This framework ensures data integrity and provides a clear lineage from raw ingestion to analytical insights.

* **Landing Zone (Raw Volumes):** Immutable backup of original API JSON responses.
* **Bronze Layer (Managed Tables):** Raw tabular representation of the source data.
* **Silver Layer (Enriched Tables):** Validated data with standardized timestamps and geospatial neighborhood tagging.
* **Gold Layer (Aggregated Tables):** KPI-focused summaries optimized for dashboard performance.

## 3. Technical Implementation Details

### A. Resilient Data Ingestion
* **Source:** Syracuse ArcGIS FeatureServer REST API.
* **Pagination Logic:** Developed a Python-based ingestion loop to bypass the 2,000-record API limit, successfully capturing the full historical dataset of **58,143 records**.
* **Schema Enforcement:** Overcame `CANNOT_MERGE_TYPE` errors by implementing a **Pandas-to-Spark transition layer**, normalizing mixed numeric types (Integers/Doubles) before table commit.

### B. The "Waterfall" Parsing Strategy (Silver Layer)
To handle inconsistent data entries from the city portal, I developed a defensive parsing function:
1.  **Primary:** Unix Epoch (milliseconds) conversion.
2.  **Secondary:** String-to-Timestamp mask parsing (e.g., `MM/dd/yyyy - hh:mma`).
3.  **Safety:** Utilized `try_cast` and `coalesce` to prevent pipeline failure on malformed input strings.

### C. Geospatial Enrichment
* **Spatial Join:** Integrated the official **Syracuse Neighborhood Boundaries** GeoJSON.
* **Point-in-Polygon Analysis:** Used **Geopandas** to perform a spatial join, tagging every individual service request with its specific neighborhood (e.g., Eastwood, Downtown, Strathmore).

## 4. Key Analytical Findings (Gold Layer)
The initial Gold Layer aggregation has already revealed significant operational insights regarding service request distribution and resolution efficiency:

| Neighborhood | Total Requests | Avg Response (Hours) | Resolution Rate |
| :--- | :--- | :--- | :--- |
| **Eastwood** | 6,160 | 120.58 | 93.00% |
| **Skunk City** | 1,495 | 83.07 | 95.05% |
| **Downtown** | 1,207 | 339.99 | 88.98% |
| **Franklin Square** | 191 | 446.34 | 80.10% |

**Insight:** There is a 437% variance in response times between the most efficient and least efficient neighborhoods, indicating a high potential for operational optimization.

## 5. Challenges Overcome
* **API Stability:** Resolved "400 Invalid URL" errors by identifying active service endpoints through metadata inspection.
* **Data Heterogeneity:** Engineered a resilient pipeline capable of processing mixed data types without manual intervention.
* **Governance:** Migrated from legacy DBFS storage to **Unity Catalog**, ensuring the project meets modern data security and governance standards.

## 6. Next Steps
* **Week 3-4:** Implementation of Time-Series analysis (Gold Trends).
* **Week 5:** Feature Engineering for Predictive Resolution Modeling.
* **Week 6:** Streamlit Dashboard integration.
