"""
Databricks connection utilities
"""
from databricks import sql
import pandas as pd
import streamlit as st
from typing import Optional

class DatabricksConnector:
    """Handle Databricks SQL connections"""
    
    def __init__(self):
        """Initialize connection using Streamlit secrets"""
        self.connection = None
        
    def connect(self):
        """Establish connection to Databricks"""
        try:
            self.connection = sql.connect(
                server_hostname=st.secrets["databricks"]["host"],
                http_path=st.secrets["databricks"]["http_path"],
                access_token=st.secrets["databricks"]["token"]
            )
            return True
        except Exception as e:
            st.error(f"Failed to connect to Databricks: {e}")
            return False
    
    def query(self, sql_query: str) -> Optional[pd.DataFrame]:
        """
        Execute SQL query and return results as DataFrame
        
        Parameters:
        -----------
        sql_query : str
            SQL query to execute
            
        Returns:
        --------
        pd.DataFrame or None
        """
        if not self.connection:
            if not self.connect():
                return None
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql_query)
            
            # Fetch results
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            cursor.close()
            
            # Convert to DataFrame
            df = pd.DataFrame(result, columns=columns)
            return df
            
        except Exception as e:
            st.error(f"Query failed: {e}")
            return None
    
    def close(self):
        """Close connection"""
        if self.connection:
            self.connection.close()