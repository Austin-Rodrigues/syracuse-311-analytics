"""
Syracuse 311 Analytics Dashboard
Main application file
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import (
    load_gold_categories,
    load_gold_agencies,
    load_gold_daily_trends,
    load_gold_hourly_patterns
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
    st.caption("**Data Pipeline:**")
    st.caption("• Bronze: 58,143 raw records")
    st.caption("• Silver: Enhanced & validated")
    st.caption("• Gold: 4 aggregated tables")
    st.markdown("---")
    st.caption("Data Source: Syracuse Open Data Portal")
    st.caption("Platform: Databricks Unity Catalog")
    st.caption("Last Updated: March 1, 2026")

# Main content
st.title("🏙️ Syracuse 311 Service Request Analytics")
st.markdown("**Real-time insights into municipal service delivery across 107 categories and 17 agencies**")

# Load data
with st.spinner("Loading data from Databricks..."):
    df_categories = load_gold_categories()
    df_agencies = load_gold_agencies()
    df_trends = load_gold_daily_trends()
    df_hourly = load_gold_hourly_patterns()

# Check if data loaded
if df_categories is None or df_categories.empty:
    st.error("❌ Failed to load data from Databricks.")
    st.info("**Troubleshooting:** Check your `.streamlit/secrets.toml` credentials")
    st.stop()

st.success("✅ Connected to Databricks Gold Layer!")

# KPI Row
st.markdown("### 📊 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_requests = df_categories['Total_Requests'].sum()
    st.metric("Total Requests", f"{total_requests:,}")

with col2:
    avg_response = df_categories['Avg_Response_Hours'].mean()
    st.metric("Avg Response Time", f"{avg_response:.1f} hrs")

with col3:
    avg_resolution = df_categories['Resolution_Rate'].mean()
    st.metric("Avg Resolution Rate", f"{avg_resolution:.1%}")

with col4:
    num_categories = len(df_categories)
    st.metric("Request Categories", num_categories)

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🏢 Agencies", "📈 Trends", "🤖 AI Assistant"])

# ===== TAB 1: OVERVIEW =====
with tab1:
    st.subheader("📋 Request Categories Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Top 15 Categories by Volume**")
        fig_categories = px.bar(
            df_categories.head(15),
            x='Total_Requests',
            y='Category',
            orientation='h',
            color='Avg_Response_Hours',
            color_continuous_scale='RdYlGn_r',
            labels={'Avg_Response_Hours': 'Avg Response (hrs)', 'Total_Requests': 'Total Requests'}
        )
        fig_categories.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_categories, use_container_width=True)
    
    with col2:
        st.markdown("**Resolution Rate by Category (Top 15)**")
        fig_resolution = px.bar(
            df_categories.head(15).sort_values('Resolution_Rate'),
            x='Resolution_Rate',
            y='Category',
            orientation='h',
            color='Resolution_Rate',
            color_continuous_scale='Greens',
            labels={'Resolution_Rate': 'Resolution Rate'}
        )
        fig_resolution.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_resolution, use_container_width=True)
    
    # Full table
    st.markdown("### 📋 All Categories - Detailed View")
    
    # Add search
    search = st.text_input("🔍 Search categories", "")
    if search:
        filtered_df = df_categories[df_categories['Category'].str.contains(search, case=False, na=False)]
    else:
        filtered_df = df_categories
    
    st.dataframe(
        filtered_df.style.format({
            'Total_Requests': '{:,.0f}',
            'Closed_Requests': '{:,.0f}',
            'Open_Requests': '{:,.0f}',
            'Avg_Response_Hours': '{:.1f}',
            'Median_Response_Hours': '{:.1f}',
            'Resolution_Rate': '{:.1%}',
            'Acknowledgment_Rate': '{:.1%}'
        }).background_gradient(subset=['Avg_Response_Hours'], cmap='RdYlGn_r'),
        use_container_width=True,
        height=400
    )

# ===== TAB 2: AGENCIES =====
with tab2:
    st.subheader("🏢 City Agency Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Request Volume by Agency**")
        fig_agency_volume = px.bar(
            df_agencies,
            x='Total_Requests',
            y='Agency',
            orientation='h',
            color='Total_Requests',
            color_continuous_scale='Blues'
        )
        fig_agency_volume.update_layout(height=500, yaxis={'categoryorder':'total ascending'}, showlegend=False)
        st.plotly_chart(fig_agency_volume, use_container_width=True)
    
    with col2:
        st.markdown("**Response Time by Agency**")
        fig_agency_response = px.bar(
            df_agencies.sort_values('Avg_Response_Hours'),
            x='Avg_Response_Hours',
            y='Agency',
            orientation='h',
            color='Avg_Response_Hours',
            color_continuous_scale='RdYlGn_r'
        )
        fig_agency_response.update_layout(height=500, yaxis={'categoryorder':'total ascending'}, showlegend=False)
        st.plotly_chart(fig_agency_response, use_container_width=True)
    
    # Agency comparison table
    st.markdown("### 📊 Agency Comparison Table")
    st.dataframe(
        df_agencies.style.format({
            'Total_Requests': '{:,.0f}',
            'Closed_Requests': '{:,.0f}',
            'Avg_Response_Hours': '{:.1f}',
            'Resolution_Rate': '{:.1%}',
            'Categories_Handled': '{:.0f}'
        }).background_gradient(subset=['Resolution_Rate'], cmap='Greens'),
        use_container_width=True,
        height=400
    )

# ===== TAB 3: TRENDS =====
with tab3:
    st.subheader("📈 Temporal Patterns & Trends")
    
    # Daily trends
    st.markdown("**📅 Daily Request Volume (Last 365 Days)**")
    if df_trends is not None and not df_trends.empty:
        fig_daily = go.Figure()
        fig_daily.add_trace(go.Scatter(
            x=df_trends['request_date'],
            y=df_trends['total_requests'],
            mode='lines',
            name='Total Requests',
            line=dict(color='steelblue', width=2)
        ))
        fig_daily.add_trace(go.Scatter(
            x=df_trends['request_date'],
            y=df_trends['closed_requests'],
            mode='lines',
            name='Closed Requests',
            line=dict(color='green', width=2)
        ))
        fig_daily.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Requests",
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig_daily, use_container_width=True)
    
    # Hourly heatmap
    st.markdown("**🔥 Request Heatmap: Hour of Day × Day of Week**")
    if df_hourly is not None and not df_hourly.empty:
        # Pivot for heatmap
        pivot = df_hourly.pivot_table(
            values='total_requests',
            index='hour',
            columns='day_name',
            aggfunc='sum',
            fill_value=0
        )
        
        # Reorder days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        pivot = pivot[[col for col in day_order if col in pivot.columns]]
        
        fig_heatmap = px.imshow(
            pivot,
            labels=dict(x="Day of Week", y="Hour of Day", color="Requests"),
            x=pivot.columns,
            y=pivot.index,
            color_continuous_scale='YlOrRd',
            aspect='auto'
        )
        fig_heatmap.update_layout(height=500)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        if df_trends is not None and not df_trends.empty:
            peak_day = df_trends.loc[df_trends['total_requests'].idxmax(), 'request_date']
            peak_count = df_trends['total_requests'].max()
            st.metric("Peak Day", f"{peak_day}", f"{peak_count} requests")
    
    with col2:
        if df_hourly is not None and not df_hourly.empty:
            busiest_hour = df_hourly.groupby('hour')['total_requests'].sum().idxmax()
            st.metric("Busiest Hour", f"{busiest_hour}:00")
    
    with col3:
        if df_trends is not None and not df_trends.empty:
            recent_avg = df_trends.tail(30)['total_requests'].mean()
            st.metric("30-Day Avg", f"{recent_avg:.0f} requests/day")

# ===== TAB 4: AI ASSISTANT =====
with tab4:
    st.subheader("🤖 AI-Powered Data Assistant")
    st.info("💡 Ask questions about Syracuse 311 data in natural language!")
    
    st.markdown("**Example questions:**")
    examples = [
        "Which category has the most requests?",
        "What's the average response time for trash collection?",
        "Show me agency performance comparison",
        "Which agencies handle the most categories?",
        "What are the peak hours for service requests?"
    ]
    
    for example in examples:
        st.markdown(f"• {example}")
    
    st.markdown("---")
    
    # Check if chatbot is configured
    try:
        from utils.chatbot import Syracuse311Chatbot
        
        # Initialize chatbot
        @st.cache_resource
        def load_chatbot():
            return Syracuse311Chatbot()
        
        chatbot = load_chatbot()
        
        if chatbot.client:
            st.success("✅ AI Assistant is ready!")
            question = st.text_input("Ask your question:", placeholder="e.g., Which category has the slowest response time?")
            
            if st.button("🚀 Ask", type="primary") and question:
                with st.spinner("🤔 Thinking..."):
                    result = chatbot.chat(question)
                    
                    if result.get("error"):
                        st.error(f"❌ {result['error']}")
                    else:
                        # Show SQL
                        with st.expander("📝 Generated SQL Query"):
                            st.code(result["sql_query"], language="sql")
                        
                        # Show results
                        if result["data"] is not None:
                            st.markdown("**📊 Results:**")
                            st.dataframe(result["data"], use_container_width=True)
                            
                            # Show analysis
                            if result["analysis"]:
                                st.markdown("**🧠 AI Analysis:**")
                                st.info(result["analysis"])
        else:
            st.warning("⚠️ AI Assistant requires Anthropic API key. Add to `.streamlit/secrets.toml`")
    except ImportError:
        st.warning("⚠️ AI Assistant module not found. Make sure `utils/chatbot.py` exists.")

# Footer
st.markdown("---")
st.caption("🏙️ Syracuse 311 Analytics Dashboard | Powered by Databricks Unity Catalog & Streamlit")
st.caption("📊 Data: 58K+ requests | 107 categories | 17 agencies | 1,101 days of history")