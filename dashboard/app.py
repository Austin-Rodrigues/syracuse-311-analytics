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
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Seal_of_Syracuse%2C_New_York.svg/200px-Seal_of_Syracuse%2C_New_York.svg.png", width=150)
    st.title("Syracuse 311")
    st.markdown("### Real-Time Analytics Dashboard")
    st.markdown("---")
    
    # Data refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.caption("Data updated: March 1, 2026")
    st.caption("Source: Syracuse Open Data Portal")

# Main content
st.title("🏙️ Syracuse 311 Service Request Analytics")
st.markdown("**Real-time insights into municipal service delivery**")

# Load data
with st.spinner("Loading data from Databricks..."):
    df_neighborhoods = load_gold_neighborhoods()
    df_trends = load_request_trends()
    df_categories = load_category_distribution()
    df_temporal = load_temporal_patterns()

# Check if data loaded successfully
if df_neighborhoods is None:
    st.error("❌ Failed to connect to Databricks. Please check your credentials in `.streamlit/secrets.toml`")
    st.stop()

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
    st.metric("Resolution Rate", f"{avg_resolution:.1%}")

with col4:
    neighborhoods = len(df_neighborhoods)
    st.metric("Neighborhoods", neighborhoods)

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📍 Neighborhoods", "📈 Trends", "🤖 AI Assistant"])

# TAB 1: OVERVIEW
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Top 10 Neighborhoods by Request Volume")
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
        st.subheader("🏷️ Top Request Categories")
        fig_categories = px.bar(
            df_categories,
            x='request_count',
            y='Category',
            orientation='h',
            color='avg_response_hours',
            color_continuous_scale='Viridis',
            labels={'avg_response_hours': 'Avg Response (hrs)', 'request_count': 'Count'}
        )
        fig_categories.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_categories, use_container_width=True)
    
    # Time series
    st.subheader("📈 Request Volume Over Time")
    fig_trends = go.Figure()
    fig_trends.add_trace(go.Scatter(
        x=df_trends['date'],
        y=df_trends['request_count'],
        mode='lines',
        name='Daily Requests',
        line=dict(color='steelblue', width=2)
    ))
    fig_trends.update_layout(
        xaxis_title="Date",
        yaxis_title="Number of Requests",
        hovermode='x unified',
        height=350
    )
    st.plotly_chart(fig_trends, use_container_width=True)

# TAB 2: NEIGHBORHOODS
with tab2:
    st.subheader("📍 Neighborhood Performance Comparison")
    
    # Filters
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("🔍 Search neighborhoods", "")
    with col2:
        sort_by = st.selectbox("Sort by", ["Total_Requests", "Avg_Response_Hours", "Resolution_Rate"])
    
    # Filter data
    if search:
        filtered_df = df_neighborhoods[df_neighborhoods['Neighborhood'].str.contains(search, case=False)]
    else:
        filtered_df = df_neighborhoods
    
    filtered_df = filtered_df.sort_values(sort_by, ascending=False)
    
    # Display table
    st.dataframe(
        filtered_df.style.format({
            'Total_Requests': '{:,.0f}',
            'Avg_Response_Hours': '{:.1f}',
            'Resolution_Rate': '{:.1%}',
            'Median_Response_Hours': '{:.1f}'
        }).background_gradient(subset=['Avg_Response_Hours'], cmap='RdYlGn_r'),
        use_container_width=True,
        height=400
    )
    
    # Response time distribution
    st.subheader("⏱️ Response Time Distribution")
    fig_response = px.box(
        filtered_df,
        y='Avg_Response_Hours',
        x='Neighborhood',
        points='all',
        color='Neighborhood',
        labels={'Avg_Response_Hours': 'Response Time (hours)'}
    )
    fig_response.update_layout(showlegend=False, height=400)
    fig_response.update_xaxes(tickangle=45)
    st.plotly_chart(fig_response, use_container_width=True)

# TAB 3: TRENDS
with tab3:
    st.subheader("📈 Temporal Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🕐 Requests by Hour of Day**")
        hourly = df_temporal.groupby('hour')['request_count'].sum().reset_index()
        fig_hourly = px.bar(
            hourly,
            x='hour',
            y='request_count',
            labels={'hour': 'Hour of Day', 'request_count': 'Total Requests'},
            color='request_count',
            color_continuous_scale='Blues'
        )
        fig_hourly.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig_hourly, use_container_width=True)
    
    with col2:
        st.markdown("**📅 Requests by Day of Week**")
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        daily = df_temporal.groupby('day_of_week')['request_count'].sum().reset_index()
        daily['day_name'] = daily['day_of_week'].apply(lambda x: day_names[x] if 0 <= x <= 6 else f"Day {x}")
        fig_daily = px.bar(
            daily,
            x='day_name',
            y='request_count',
            labels={'day_name': 'Day of Week', 'request_count': 'Total Requests'},
            color='request_count',
            color_continuous_scale='Greens'
        )
        fig_daily.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig_daily, use_container_width=True)
    
    # Heatmap
    st.markdown("**🔥 Request Heatmap: Hour × Day of Week**")
    pivot = df_temporal.pivot_table(
        values='request_count',
        index='hour',
        columns='day_of_week',
        aggfunc='sum'
    ).fillna(0)
    
    fig_heatmap = px.imshow(
        pivot,
        labels=dict(x="Day of Week", y="Hour of Day", color="Requests"),
        x=[day_names[i] if i < 7 else f"Day {i}" for i in pivot.columns],
        y=pivot.index,
        color_continuous_scale='YlOrRd',
        aspect='auto'
    )
    fig_heatmap.update_layout(height=500)
    st.plotly_chart(fig_heatmap, use_container_width=True)

# TAB 4: AI ASSISTANT (Placeholder for now)
with tab4:
    st.subheader("🤖 AI-Powered Data Assistant")
    st.info("💡 AI Assistant coming next! Ask questions about your 311 data in plain English.")
    
    st.markdown("**Example questions you'll be able to ask:**")
    st.markdown("""
    - "Which neighborhood has the slowest response time for potholes?"
    - "Show me request trends in Eastwood over the past 3 months"
    - "What categories have the lowest resolution rates?"
    - "Compare Downtown vs Northside service delivery"
    """)
    
    st.warning("⏳ This feature will be implemented next using Claude API")