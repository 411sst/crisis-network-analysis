# Crisis Network Analysis Dashboard
# Main Streamlit Application

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

# Page configuration
st.set_page_config(
    page_title="Crisis Network Analysis",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stAlert {
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">🌐 Crisis Network Analysis Dashboard</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    # Streamlit's st.image expects `use_column_width` (not `use_container_width`)
    st.image(
        "https://via.placeholder.com/150x50/1f77b4/ffffff?text=Crisis+Analysis",
        use_column_width=True,
    )
    st.markdown("---")

    st.markdown("### 📊 Navigation")
    st.markdown("""
    Use the pages in the sidebar to:
    - 📥 **Collect Data**: Gather crisis posts from Reddit
    - 📈 **Analyze Data**: View statistics and patterns
    - 🔬 **Network Analysis**: Explore user networks
    - 🧠 **LIWC Insights**: Cognitive & emotional analysis
    - 📄 **Generate Reports**: Export PDF reports
    """)

    st.markdown("---")
    st.markdown("### 🎯 Quick Stats")

    # Check for existing data
    data_dir = project_root / 'data' / 'processed'
    if data_dir.exists():
        csv_files = list(data_dir.glob('*.csv'))
        st.metric("Datasets", len(csv_files))
    else:
        st.metric("Datasets", 0)

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    **Crisis Network Analysis**

    Analyze social media behavior during crisis events using:
    - Network analysis
    - LIWC cognitive analysis
    - PADM framework
    - Temporal patterns

    Version: 1.0-MVP
    """)

# Main content
st.markdown("## Welcome to Crisis Network Analysis Dashboard")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📥 Collect Data")
    st.markdown("""
    Start by collecting crisis data from Reddit.

    Navigate to **01_Data_Collection** to begin.
    """)
    if st.button("Go to Data Collection →", use_container_width=True):
        st.switch_page("pages/01_Data_Collection.py")

with col2:
    st.markdown("### 📊 Analyze")
    st.markdown("""
    View your collected data and explore patterns.

    Navigate to **02_Data_Overview** to explore.
    """)
    if st.button("View Analysis →", use_container_width=True):
        st.switch_page("pages/02_Data_Overview.py")

with col3:
    st.markdown("### 📄 Reports")
    st.markdown("""
    Generate professional PDF reports.

    Navigate to **06_Generate_Reports** to create.
    """)
    if st.button("Create Report →", use_container_width=True):
        st.switch_page("pages/06_Generate_Reports.py")

st.markdown("---")

# Quick start guide
st.markdown("## 🚀 Quick Start Guide")

with st.expander("📖 How to use this dashboard", expanded=True):
    st.markdown("""
    ### Step 1: Configure API Keys
    1. Copy `config/api_keys.env.template` to `config/api_keys.env`
    2. Add your Reddit API credentials
    3. Restart the dashboard

    ### Step 2: Collect Data
    1. Go to **01_Data_Collection** page
    2. Select a crisis event
    3. Configure collection parameters
    4. Click "Start Collection"

    ### Step 3: Analyze Data
    1. Go to **02_Data_Overview** to see your data
    2. Explore **03_Network_Analysis** for user networks
    3. Check **04_Temporal_Analysis** for time patterns
    4. Review **05_LIWC_Analysis** for cognitive insights

    ### Step 4: Generate Reports
    1. Go to **06_Generate_Reports**
    2. Select your dataset
    3. Choose report type
    4. Export as PDF or HTML
    """)

# System status
st.markdown("---")
st.markdown("## 🔧 System Status")

col1, col2, col3, col4 = st.columns(4)

with col1:
    # Check if config exists
    config_file = project_root / 'config' / 'api_keys.env'
    if config_file.exists():
        st.success("✅ Config Found")
    else:
        st.warning("⚠️ Config Needed")

with col2:
    # Check for data
    processed_dir = project_root / 'data' / 'processed'
    if processed_dir.exists() and list(processed_dir.glob('*.csv')):
        st.success("✅ Data Available")
    else:
        st.info("ℹ️ No Data Yet")

with col3:
    # Check dependencies
    try:
        import pandas
        import networkx
        import plotly
        st.success("✅ Dependencies OK")
    except ImportError:
        st.error("❌ Missing Deps")

with col4:
    # Check results directory
    results_dir = project_root / 'results' / 'networks'
    if results_dir.exists() and list(results_dir.glob('*.json')):
        st.success("✅ Results Found")
    else:
        st.info("ℹ️ No Results Yet")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>Crisis Network Analysis Dashboard v1.0 | Built with Streamlit |
    <a href='https://github.com/411sst/crisis-network-analysis'>GitHub</a></p>
</div>
""", unsafe_allow_html=True)
