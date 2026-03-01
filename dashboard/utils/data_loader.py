"""
Data loading utilities for Gold layer tables
"""
import pandas as pd
import streamlit as st
from .db_connector import DatabricksConnector

@st.cache_data(ttl=3600)
def load_gold_categories():
    """Load category performance data from Gold layer"""
    
    query = """
    SELECT 
        Category,
        total_requests,
        closed_requests,
        open_requests,
        avg_response_hours,
        median_response_hours,
        percent_closed,
        percent_acknowledged,
        primary_agency
    FROM workspace.syracuse_project.gold_category_performance
    ORDER BY total_requests DESC
    """
    
    connector = DatabricksConnector()
    df = connector.query(query)
    connector.close()
    
    if df is not None:
        # Rename for consistency
        df = df.rename(columns={
            'Category': 'Category',
            'total_requests': 'Total_Requests',
            'closed_requests': 'Closed_Requests',
            'open_requests': 'Open_Requests',
            'avg_response_hours': 'Avg_Response_Hours',
            'median_response_hours': 'Median_Response_Hours',
            'percent_closed': 'Resolution_Rate',
            'percent_acknowledged': 'Acknowledgment_Rate',
            'primary_agency': 'Primary_Agency'
        })
    
    return df

@st.cache_data(ttl=3600)
def load_gold_agencies():
    """Load agency performance data"""
    
    query = """
    SELECT 
        Agency_Name,
        total_requests,
        closed_requests,
        avg_response_hours,
        percent_closed,
        categories_handled
    FROM workspace.syracuse_project.gold_agency_performance
    ORDER BY total_requests DESC
    """
    
    connector = DatabricksConnector()
    df = connector.query(query)
    connector.close()
    
    if df is not None:
        df = df.rename(columns={
            'Agency_Name': 'Agency',
            'total_requests': 'Total_Requests',
            'closed_requests': 'Closed_Requests',
            'avg_response_hours': 'Avg_Response_Hours',
            'percent_closed': 'Resolution_Rate',
            'categories_handled': 'Categories_Handled'
        })
    
    return df

@st.cache_data(ttl=3600)
def load_gold_daily_trends():
    """Load daily trend data"""
    
    query = """
    SELECT 
        request_date,
        total_requests,
        closed_requests,
        avg_response_hours,
        categories_active,
        agencies_active
    FROM workspace.syracuse_project.gold_daily_trends
    WHERE request_date >= DATE_SUB(CURRENT_DATE(), 365)
    ORDER BY request_date
    """
    
    connector = DatabricksConnector()
    df = connector.query(query)
    connector.close()
    
    return df

@st.cache_data(ttl=3600)
def load_gold_hourly_patterns():
    """Load hourly pattern data"""
    
    query = """
    SELECT 
        created_hour as hour,
        day_name,
        total_requests,
        avg_response_hours
    FROM workspace.syracuse_project.gold_hourly_patterns
    ORDER BY created_hour, day_name
    """
    
    connector = DatabricksConnector()
    df = connector.query(query)
    connector.close()
    
    return df

def execute_custom_query(sql_query: str) -> pd.DataFrame:
    """
    Execute custom SQL query (for chatbot)
    NO CACHING - for dynamic queries
    """
    connector = DatabricksConnector()
    df = connector.query(sql_query)
    connector.close()
    return df