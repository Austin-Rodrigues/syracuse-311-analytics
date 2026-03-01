"""
Syracuse 311 Analytics Dashboard
Main application file
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import (
    load_gold_neighborhoods,
    load_request_trends,
    load_category_distribution,
    load_temporal_patterns
)

# Page config
st.set_page_config(
    page_title="Syracuse 311 Analytics",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🏙️ Syracuse 311")
    st.markdown("### Real-Time Analytics Dashboard")
    st.markdown("---")
    
    # Data refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.caption("Data Source: Syracuse Open Data Portal")
    st.caption("Connected to: Databricks Unity Catalog")

# Main content
st.title("🏙️ Syracuse 311 Service Request Analytics")
st.markdown("**Real-time insights into municipal service delivery**")

# Load data
with st.spinner("Loading data from Databricks..."):
    df_neighborhoods = load_gold_neighborhoods()

# Check if data loaded successfully
if df_neighborhoods is None or df_neighborhoods.empty:
    st.error("❌ Failed to load data from Databricks.")
    st.info("**Troubleshooting:**")
    st.code("""
# Check your .streamlit/secrets.toml file:
[databricks]
host = "adb-xxxxx.azuredatabricks.net"
http_path = "/sql/1.0/warehouses/xxxxx"
token = "dapixxxxx"
    """)
    st.stop()

st.success("✅ Connected to Databricks!")

# KPI Row
st.markdown("### 📊 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_requests = df_neighborhoods['Total_Requests'].sum()
    st.metric("Total Requests", f"{total_requests:,}")

with col2:
    avg_response = df_neighborhoods['Avg_Response_Hours'].mean()
    st.metric("Avg Response Time", f"{avg_response:.1f} hrs")

with col3:
    avg_resolution = df_neighborhoods['Resolution_Rate'].mean()
    st.metric("Avg Resolution Rate", f"{avg_resolution:.1%}")

with col4:
    neighborhoods = len(df_neighborhoods)
    st.metric("Neighborhoods", neighborhoods)

st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Overview", "📍 Neighborhoods", "🤖 AI Assistant"])

# TAB 1: OVERVIEW
with tab1:
    st.subheader("📍 Neighborhood Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Top 10 by Request Volume**")
        fig_neighborhoods = px.bar(
            df_neighborhoods.head(10),
            x='Total_Requests',
            y='Neighborhood',
            orientation='h',
            color='Avg_Response_Hours',
            color_continuous_scale='RdYlGn_r',
            labels={'Avg_Response_Hours': 'Avg Response (hrs)'}
        )
        fig_neighborhoods.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_neighborhoods, use_container_width=True)
    
    with col2:
        st.markdown("**Response Time Distribution**")
        fig_response = px.box(
            df_neighborhoods,
            y='Avg_Response_Hours',
            points='all',
            labels={'Avg_Response_Hours': 'Response Time (hours)'}
        )
        fig_response.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_response, use_container_width=True)
    
    # Summary table
    st.subheader("📋 All Neighborhoods")
    st.dataframe(
        df_neighborhoods.style.format({
            'Total_Requests': '{:,.0f}',
            'Avg_Response_Hours': '{:.1f}',
            'Resolution_Rate': '{:.1%}'
        }).background_gradient(subset=['Avg_Response_Hours'], cmap='RdYlGn_r'),
        use_container_width=True,
        height=400
    )

# TAB 2: NEIGHBORHOODS
with tab2:
    st.subheader("📍 Neighborhood Comparison")
    
    # Filters
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("🔍 Search neighborhoods", "")
    with col2:
        sort_by = st.selectbox("Sort by", ["Total_Requests", "Avg_Response_Hours", "Resolution_Rate"])
    
    # Filter data
    if search:
        filtered_df = df_neighborhoods[df_neighborhoods['Neighborhood'].str.contains(search, case=False, na=False)]
    else:
        filtered_df = df_neighborhoods
    
    filtered_df = filtered_df.sort_values(sort_by, ascending=False)
    
    # Display table
    st.dataframe(
        filtered_df.style.format({
            'Total_Requests': '{:,.0f}',
            'Avg_Response_Hours': '{:.1f}',
            'Resolution_Rate': '{:.1%}'
        }).background_gradient(subset=['Avg_Response_Hours'], cmap='RdYlGn_r'),
        use_container_width=True,
        height=400
    )
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Response Time by Neighborhood**")
        fig1 = px.bar(
            filtered_df.sort_values('Avg_Response_Hours'),
            x='Avg_Response_Hours',
            y='Neighborhood',
            orientation='h',
            color='Avg_Response_Hours',
            color_continuous_scale='RdYlGn_r'
        )
        fig1.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.markdown("**Resolution Rate by Neighborhood**")
        fig2 = px.bar(
            filtered_df.sort_values('Resolution_Rate'),
            x='Resolution_Rate',
            y='Neighborhood',
            orientation='h',
            color='Resolution_Rate',
            color_continuous_scale='Greens'
        )
        fig2.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

# TAB 3: AI ASSISTANT (Placeholder)
with tab3:
    st.subheader("🤖 AI-Powered Assistant")
    st.info("💡 AI Assistant will be added next! You'll be able to ask questions in natural language.")
    
    st.markdown("**Example questions (coming soon):**")
    st.markdown("""
    - "Which neighborhood has the slowest response time?"
    - "Show me trends in Eastwood"
    - "Compare Downtown vs Northside"
    - "What's the average response time for potholes?"
    """)
    
    # Preview of chatbot UI
    st.text_input("Ask a question (preview)", placeholder="e.g., Which neighborhoods need the most attention?", disabled=True)
    st.button("🚀 Ask", disabled=True)

# Footer
st.markdown("---")
st.caption("🏙️ Syracuse 311 Analytics Dashboard | Data updated in real-time from Databricks")