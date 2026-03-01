"""
AI Assistant Page - Chat interface for natural language queries
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).parent.parent))

from utils.chatbot import Syracuse311Chatbot

# Page config
st.set_page_config(
    page_title="AI Assistant - Syracuse 311",
    page_icon="🤖",
    layout="wide"
)

# Title
st.title("🤖 AI-Powered Data Assistant")
st.markdown("Ask questions about Syracuse 311 data in plain English!")

# Initialize chatbot
@st.cache_resource
def load_chatbot():
    return Syracuse311Chatbot()

chatbot = load_chatbot()

# Check if API key is configured
if not chatbot.client:
    st.error("⚠️ Anthropic API key not configured. Please add it to `.streamlit/secrets.toml`")
    st.code("""
# Add to .streamlit/secrets.toml:
[anthropic]
api_key = "sk-ant-..."
    """)
    st.stop()

# Sidebar with examples
with st.sidebar:
    st.markdown("### 💡 Example Questions")
    
    example_questions = [
        "Which neighborhood has the slowest response time?",
        "Show me the top 10 request categories",
        "How many potholes were reported in Eastwood?",
        "What's the average response time for sewer issues?",
        "Compare Downtown vs Northside resolution rates",
        "Show me request trends over the past year",
        "Which agencies handle the most requests?",
        "What are the peak hours for service requests?",
        "List neighborhoods with resolution rates below 90%",
        "How many requests were closed in February 2025?"
    ]
    
    for i, question in enumerate(example_questions):
        if st.button(f"📌 {question}", key=f"example_{i}", use_container_width=True):
            st.session_state.current_question = question

    st.markdown("---")
    st.markdown("### ℹ️ How It Works")
    st.markdown("""
    1. **Ask** your question in plain English
    2. **AI generates** SQL query from your question
    3. **Query executes** on your Databricks data
    4. **AI analyzes** results and provides insights
    """)

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "current_question" not in st.session_state:
    st.session_state.current_question = ""

# Main chat interface
st.markdown("### 💬 Ask Your Question")

# Chat input
question = st.text_input(
    "Enter your question:",
    value=st.session_state.current_question,
    placeholder="e.g., Which neighborhoods have the highest request volumes?",
    key="question_input"
)

# Buttons
col1, col2 = st.columns([1, 5])
with col1:
    ask_button = st.button("🚀 Ask", type="primary", use_container_width=True)
with col2:
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.current_question = ""
        st.rerun()

# Process question
if ask_button and question:
    # Get response from chatbot
    result = chatbot.chat(question)
    
    # Add to history
    st.session_state.chat_history.append({
        "question": question,
        "result": result
    })
    
    # Clear current question
    st.session_state.current_question = ""

# Display chat history (most recent first)
if st.session_state.chat_history:
    st.markdown("---")
    st.markdown("### 📜 Conversation History")
    
    for i, chat in enumerate(reversed(st.session_state.chat_history)):
        with st.container():
            # Question
            st.markdown(f"**🙋 You asked:** {chat['question']}")
            
            result = chat['result']
            
            # Error handling
            if result.get("error"):
                st.error(f"❌ {result['error']}")
            else:
                # Show SQL query in expander
                with st.expander("📝 View SQL Query"):
                    st.code(result["sql_query"], language="sql")
                
                # Show data
                if result["data"] is not None and not result["data"].empty:
                    st.markdown("**📊 Results:**")
                    
                    # Display data
                    st.dataframe(
                        result["data"],
                        use_container_width=True,
                        height=min(400, len(result["data"]) * 35 + 38)
                    )
                    
                    # Show analysis
                    if result["analysis"]:
                        st.markdown("**🧠 AI Analysis:**")
                        st.info(result["analysis"])
                    
                    # Download button
                    csv = result["data"].to_csv(index=False)
                    st.download_button(
                        "⬇️ Download Results (CSV)",
                        csv,
                        f"syracuse_311_query_{i}.csv",
                        "text/csv",
                        key=f"download_{i}"
                    )
                else:
                    st.warning("No results found")
            
            st.markdown("---")
else:
    # Show welcome message when no history
    st.info("👋 Welcome! Ask a question to get started, or try one of the example questions in the sidebar.")

# Footer
st.markdown("---")
st.caption("💡 Powered by Claude AI | Data from Syracuse Open Data Portal")