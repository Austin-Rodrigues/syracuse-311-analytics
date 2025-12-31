# Syracuse 311 Real-Time Service Request Analytics Pipeline
  
**Status:** Infrastructure Setup Complete

---

## Project Overview

An automated data analytics pipeline that processes Syracuse's 311 service request data to provide actionable insights for city officials, neighborhood associations, and residents. The system includes four advanced analytical capabilities: anomaly detection, predictive response time modeling, neighborhood comparison analysis, and seasonal pattern identification.

### Problem Statement

Syracuse receives thousands of 311 service requests annually for issues like potholes, trash collection, street signs, and more. Currently, this data is not systematically analyzed to:
- Detect unusual spikes in request volumes
- Predict resolution times for resource planning
- Compare service levels across neighborhoods
- Identify seasonal patterns for proactive maintenance

### Solution

A production-ready data pipeline that:
1. Automatically extracts data from Syracuse Open Data portal
2. Cleans and validates municipal data
3. Performs statistical and machine learning analysis
4. Visualizes insights in an interactive dashboard
5. Provides reproducible, documented analysis

---

## Key Features (Planned)

### Completed (Week 1)
- [x] ArcGIS REST API client for data extraction
- [x] Raw data preservation architecture
- [x] Metadata tracking system
- [x] Professional project structure

### In Progress (Week 2)
- [ ] Data cleaning pipeline
- [ ] Data validation framework
- [ ] ETL orchestration

### Upcoming (Weeks 3-9)
- [ ] **Enhancement #1:** Anomaly Detection (statistical methods)
- [ ] **Enhancement #2:** Predictive Response Time Model (regression)
- [ ] **Enhancement #3:** Neighborhood Comparison Analysis (geospatial)
- [ ] **Enhancement #4:** Seasonal Pattern Analysis (time-series)
- [ ] Interactive Streamlit dashboard
- [ ] Complete documentation

---

## Architecture

### Data Flow
```
Syracuse Open Data Portal (ArcGIS API)
    ↓
API Client (data_ingestion/)
    ↓
Raw Data Storage (data/raw/) ← IMMUTABLE
    ↓
Data Cleaning Pipeline (data_processing/)
    ↓
Processed Data (data/processed/)
    ↓
Analysis Layer (src/analysis/)
    ↓
Visualization Dashboard (Streamlit)
```

### Technology Stack
- **Language:** Python 3.11+
- **Data Processing:** pandas, numpy
- **API Integration:** requests
- **Geospatial:** geopandas, folium
- **Machine Learning:** scikit-learn
- **Visualization:** matplotlib, seaborn, plotly
- **Dashboard:** Streamlit
- **Database:** SQLite
- **Version Control:** Git/GitHub

---

## Dataset Information

**Source:** Syracuse Open Data Portal  
**Dataset:** SYRCityline Requests (2021-Present)  
**API:** ArcGIS REST Services  
**Records:** 50,000+ service requests  
**Coverage:** July 2021 - Present  
**Update Frequency:** Daily

### Available Fields (19 total)
- `Id` - Unique request identifier
- `Category` - Request type (Pothole, Trash, Street Sign, etc.)
- `Summary` - Brief description
- `Address` - Location
- `Lat`, `Lng` - Geographic coordinates
- `Created_at_local` - Request submission timestamp
- `Acknowledged_at_local` - City acknowledgment timestamp
- `Closed_at_local` - Resolution timestamp
- `Minutes_to_Acknowledge` - Time to first response
- `Minutes_to_Close` - Time to resolution
- `Agency_Name` - Responsible city department
- `Rating` - User satisfaction rating
- Additional metadata fields

---

## Getting Started

### Prerequisites
- Python 3.11 or higher
- pip package manager
- Git

### Installation

1. **Clone the repository**
```bash
git clone [repo-url]
cd syracuse-311-analytics
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Usage

**Fetch raw data:**
```bash
cd src/data_ingestion
python arcgis_api.py
```

This will:
- Connect to Syracuse Open Data API
- Fetch sample records
- Save raw data to `data/raw/`
- Generate metadata file

**Check the data:**
```bash
# View the CSV
cd ../../data/raw
cat sample_raw_data.csv

# View metadata
cat sample_raw_data_metadata.json
```

---

## Project Structure

```
syracuse-311-analytics/
├── .gitignore                  # Prevents committing sensitive data
├── README.md                   # This file
├── requirements.txt            # Python dependencies
│
├── data/
│   ├── raw/                    # Raw data from API (not in git)
│   ├── processed/              # Cleaned data (not in git)
│   └── features/               # Engineered features (not in git)
│
├── src/
│   ├── data_ingestion/
│   │   ├── __init__.py
│   │   └── arcgis_api.py      # API client (COMPLETED)
│   │
│   ├── data_processing/
│   │   ├── __init__.py
│   │   ├── cleaners.py        # Data cleaning (IN PROGRESS)
│   │   └── validators.py      # Data validation (IN PROGRESS)
│   │
│   ├── data_pipeline/
│   │   └── etl_pipeline.py    # ETL orchestration (PLANNED)
│   │
│   └── analysis/
│       ├── anomaly_detection.py       # Enhancement #1 (PLANNED)
│       ├── response_time_model.py     # Enhancement #2 (PLANNED)
│       ├── neighborhood_analysis.py   # Enhancement #3 (PLANNED)
│       └── seasonal_patterns.py       # Enhancement #4 (PLANNED)
│
├── notebooks/
│   ├── 01_raw_data_exploration.ipynb
│   └── 02_data_quality_assessment.ipynb
│
├── docs/
│   ├── proposal.md             # Project proposal (IN PROGRESS)
│   └── architecture.md         # System architecture (IN PROGRESS)
│
└── dashboard/
    └── app.py                  # Streamlit dashboard (PLANNED)
```

---

## Timeline

| Week | Dates | Focus | Status |
|------|-------|-------|--------|
| 1 | Dec 30-Jan 5 | Infrastructure Setup | Complete |
| 2 | Jan 6-12 | Data Cleaning Pipeline | In Progress |
| 3 | Jan 13-19 | Core Analytics | Planned |
| 4 | Jan 20-26 | Anomaly Detection | Planned |
| 5 | Jan 27-Feb 2 | Predictive Modeling | Planned |
| 6 | Feb 3-9 | Neighborhood Analysis | Planned |
| 7 | Feb 10-16 | Seasonal Patterns | Planned |
| 8 | Feb 17-23 | Dashboard Development | Planned |
| 9 | Feb 24-28 | Documentation & Polish | Planned |

**Project Deadline:** February 28, 2025

---

## Data Quality Considerations

From initial exploration, we've identified these data quality issues to address in the cleaning pipeline:

1. **Date Format Issues:** `Created_at_local`, `Acknowledged_at_local`, `Closed_at_local` are strings requiring datetime parsing
2. **Type Inconsistencies:** `Minutes_to_Close` stored as string despite numeric content
3. **Missing Values:** Various fields have incomplete data
4. **Coordinate Validation:** Need to verify Lat/Lng values are within Syracuse bounds
5. **Duplicate Detection:** Check for duplicate request IDs

---

## Development Principles

- **Raw Data is Sacred:** Never modify original data; all transformations are documented
- **Reproducibility:** All analysis can be re-run from raw data
- **Separation of Concerns:** Clear boundaries between ingestion, processing, and analysis
- **Documentation:** Code is well-commented; architectural decisions are recorded
- **Version Control:** Meaningful commit messages; feature branches for enhancements
- **Testing:** Critical calculations are validated against ground truth

---

## Skills Demonstrated

- **Data Engineering:** ETL pipeline design, data validation, schema management
- **API Integration:** REST API consumption, pagination, error handling
- **Data Analysis:** Statistical methods, time-series analysis, geospatial analysis
- **Machine Learning:** Regression modeling, feature engineering
- **Software Engineering:** Modular design, version control, documentation
- **Data Visualization:** Interactive dashboards, map-based visualization
- **Project Management:** Timeline planning, milestone tracking

---
 
For questions or collaboration opportunities, please contact via GitHub.

---

## License

This project is developed for academic and civic purposes as part of the Syracuse Open Data initiative.

---

## Acknowledgments

- Syracuse Open Data Portal for providing public dataset access
- City of Syracuse Office of Accountability, Performance and Innovation
- Syracuse University for OPT research support

---

**Last Updated:** December 30, 2024  
**Current Status:** Week 2 Complete - API Client Operational
