"""
Data loading utilities for Gold layer tables
"""
import pandas as pd
import streamlit as st
from .db_connector import DatabricksConnector

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_gold_neighborhoods():
    """Load neighborhood performance data from Gold layer"""
    
    query = """
    SELECT 
        neighborhood,
        total_requests,
        avg_response_hours,
        percent_closed
    FROM workspace.syracuse_project.gold_neighborhood_performance
    ORDER BY total_requests DESC
    """
    
    connector = DatabricksConnector()
    df = connector.query(query)
    connector.close()
    
    if df is not None:
        # Rename columns to match app expectations (Title Case)
        df = df.rename(columns={
            'neighborhood': 'Neighborhood',
            'total_requests': 'Total_Requests',
            'avg_response_hours': 'Avg_Response_Hours',
            'percent_closed': 'Resolution_Rate'
        })
    
    return df

@st.cache_data(ttl=3600)
def load_request_trends():
    """Load request volume trends over time"""
    
    query = """
    SELECT 
        DATE(created_at) as date,
        COUNT(*) as request_count,
        AVG(response_time_hours) as avg_response_hours,
        COUNT(CASE WHEN is_closed THEN 1 END) as closed_count
    FROM workspace.syracuse_project.silver_requests
    WHERE created_at >= DATE_SUB(CURRENT_DATE(), 365)
    GROUP BY DATE(created_at)
    ORDER BY date
    """
    
    connector = DatabricksConnector()
    df = connector.query(query)
    connector.close()
    
    return df

@st.cache_data(ttl=3600)
def load_category_distribution():
    """Load request distribution by category"""
    
    query = """
    SELECT 
        Category,
        COUNT(*) as request_count,
        AVG(response_time_hours) as avg_response_hours,
        AVG(CASE WHEN is_closed THEN 1.0 ELSE 0.0 END) as resolution_rate
    FROM workspace.syracuse_project.silver_requests
    GROUP BY Category
    ORDER BY request_count DESC
    LIMIT 15
    """
    
    connector = DatabricksConnector()
    df = connector.query(query)
    connector.close()
    
    return df

@st.cache_data(ttl=3600)
def load_temporal_patterns():
    """Load patterns by hour and day of week"""
    
    query = """
    SELECT 
        created_hour as hour,
        created_day_of_week as day_of_week,
        COUNT(*) as request_count,
        AVG(response_time_hours) as avg_response_hours
    FROM workspace.syracuse_project.silver_requests
    GROUP BY created_hour, created_day_of_week
    ORDER BY day_of_week, hour
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