"""
AI-Powered Chatbot for Syracuse 311 Data
Uses Claude API to answer questions about the data
"""
import streamlit as st
from anthropic import Anthropic
import pandas as pd
from typing import Optional, Dict, List
from .data_loader import execute_custom_query

class Syracuse311Chatbot:
    """
    AI chatbot that can query and analyze Syracuse 311 data
    """
    
    def __init__(self):
        """Initialize chatbot with Claude API"""
        try:
            self.client = Anthropic(api_key=st.secrets["anthropic"]["api_key"])
            self.model = "claude-sonnet-4-20250514"
        except Exception as e:
            st.error(f"Failed to initialize AI: {e}")
            self.client = None
    
    def get_schema_context(self) -> str:
        """
        Return database schema information for Claude
        """
        schema = """
        You have access to Syracuse 311 service request data in Databricks Unity Catalog.
        
        AVAILABLE TABLES:
        
        1. workspace.syracuse_project.gold_neighborhood_performance
           - Neighborhood (string): Neighborhood name
           - Total_Requests (int): Total number of requests
           - Closed_Requests (int): Number of closed requests
           - Avg_Response_Hours (float): Average response time in hours
           - Median_Response_Hours (float): Median response time in hours
           - Resolution_Rate (float): Percentage of requests closed (0-1)
           - Avg_Minutes_to_Acknowledge (float): Average time to acknowledge
        
        2. workspace.syracuse_project.silver_requests
           - Id (string): Request ID
           - Category (string): Request type (Pothole, Trash, etc.)
           - neighborhood (string): Neighborhood name
           - Agency_Name (string): Responsible city department
           - created_at (timestamp): Request creation time
           - closed_at (timestamp): Request closure time
           - is_closed (boolean): Whether request is closed
           - response_time_hours (float): Time to close in hours
           - Minutes_to_Close (float): Time to close in minutes
           - created_hour (int): Hour of day (0-23)
           - created_day_of_week (int): Day of week (0=Monday)
           - Lat, Lng (float): Geographic coordinates
           - Address (string): Request location
           - Summary (string): Request description
        
        3. workspace.syracuse_project.bronze_requests
           - Raw data (same fields as silver, less cleaned)
        
        GUIDELINES:
        - Use gold_neighborhood_performance for neighborhood-level aggregations
        - Use silver_requests for detailed request analysis
        - Date range: June 2021 - February 2025
        - Total records: ~57,000 closed requests
        - Always use proper SQL syntax for Databricks (Spark SQL)
        - Use DATE() function for date filtering
        - When counting, always consider is_closed status
        """
        return schema
    
    def generate_sql_query(self, user_question: str) -> Optional[str]:
        """
        Use Claude to generate SQL query from natural language question
        
        Parameters:
        -----------
        user_question : str
            User's question in natural language
            
        Returns:
        --------
        str : SQL query or None if failed
        """
        if not self.client:
            return None
        
        system_prompt = f"""You are an expert SQL assistant for Syracuse 311 municipal data.

{self.get_schema_context()}

Your task: Convert the user's question into a valid Spark SQL query.

RULES:
1. Return ONLY the SQL query, no explanations
2. Use proper Spark SQL syntax
3. Limit results to 100 rows max (add LIMIT 100)
4. Use appropriate aggregations (GROUP BY, AVG, COUNT, etc.)
5. For neighborhood comparisons, use gold_neighborhood_performance
6. For detailed request analysis, use silver_requests
7. Always handle NULL values appropriately
8. Use CAST() for type conversions if needed

EXAMPLE CONVERSIONS:

User: "Which neighborhood has the most requests?"
SQL: SELECT Neighborhood, Total_Requests FROM workspace.syracuse_project.gold_neighborhood_performance ORDER BY Total_Requests DESC LIMIT 10

User: "Show me pothole trends in Eastwood"
SQL: SELECT DATE(created_at) as date, COUNT(*) as count FROM workspace.syracuse_project.silver_requests WHERE Category LIKE '%Pothole%' AND neighborhood = 'Eastwood' GROUP BY DATE(created_at) ORDER BY date LIMIT 100

User: "What's the average response time for trash collection?"
SQL: SELECT AVG(response_time_hours) as avg_hours FROM workspace.syracuse_project.silver_requests WHERE Category LIKE '%Trash%' AND is_closed = true

Now convert the user's question to SQL."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": user_question
                }]
            )
            
            sql_query = response.content[0].text.strip()
            
            # Clean up the response (remove markdown code blocks if present)
            if sql_query.startswith("```sql"):
                sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            elif sql_query.startswith("```"):
                sql_query = sql_query.replace("```", "").strip()
            
            return sql_query
            
        except Exception as e:
            st.error(f"Failed to generate query: {e}")
            return None
    
    def analyze_results(self, user_question: str, sql_query: str, df: pd.DataFrame) -> str:
        """
        Use Claude to analyze query results and provide insights
        
        Parameters:
        -----------
        user_question : str
            Original user question
        sql_query : str
            SQL query that was executed
        df : pd.DataFrame
            Query results
            
        Returns:
        --------
        str : Natural language analysis
        """
        if not self.client or df is None or df.empty:
            return "No data to analyze."
        
        # Convert DataFrame to string representation (limit size)
        df_summary = df.head(20).to_string(index=False)
        
        system_prompt = """You are a data analyst for Syracuse city government. 
        Analyze query results and provide clear, actionable insights for city officials.
        
        Keep responses concise (2-4 sentences) and highlight key findings.
        Use specific numbers and comparisons.
        Suggest implications for city operations when relevant."""
        
        user_prompt = f"""Question: {user_question}

SQL Query Used:
{sql_query}

Results:
{df_summary}

Provide a clear analysis of these results. What are the key insights?"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            return f"Analysis failed: {e}"
    
    def chat(self, user_question: str) -> Dict:
        """
        Main chat interface - handles complete question-to-answer flow
        
        Parameters:
        -----------
        user_question : str
            User's question
            
        Returns:
        --------
        dict : Contains sql_query, data, analysis, error (if any)
        """
        result = {
            "sql_query": None,
            "data": None,
            "analysis": None,
            "error": None
        }
        
        # Step 1: Generate SQL query
        with st.spinner("🤔 Understanding your question..."):
            sql_query = self.generate_sql_query(user_question)
        
        if not sql_query:
            result["error"] = "Failed to generate SQL query"
            return result
        
        result["sql_query"] = sql_query
        
        # Step 2: Execute query
        with st.spinner("📊 Querying database..."):
            try:
                df = execute_custom_query(sql_query)
                result["data"] = df
            except Exception as e:
                result["error"] = f"Query execution failed: {e}"
                return result
        
        if df is None or df.empty:
            result["error"] = "Query returned no results"
            return result
        
        # Step 3: Analyze results
        with st.spinner("🧠 Analyzing results..."):
            analysis = self.analyze_results(user_question, sql_query, df)
            result["analysis"] = analysis
        
        return result