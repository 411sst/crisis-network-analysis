# Crisis Network Analysis Dashboard
# Main Streamlit Application (Home)

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

# Page configuration
st.set_page_config(
    page_title="Crisis Network Analysis System",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styling */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Main Header */
    .main-header {
        font-size: 2.8rem;
        font-weight: 600;
        color: #1a1a2e;
        text-align: center;
        padding: 2rem 0 1rem 0;
        letter-spacing: -0.5px;
        border-bottom: 2px solid #e0e0e0;
        margin-bottom: 2rem;
    }
    
    .main-subtitle {
        font-size: 1.1rem;
        font-weight: 400;
        color: #666;
        text-align: center;
        margin-top: -1.5rem;
        margin-bottom: 2rem;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #dee2e6;
    }
    
    [data-testid="stSidebar"] h3 {
        color: #2c3e50;
        font-weight: 600;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 1.5rem;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        color: white;
        margin: 1rem 0;
    }
    
    .metric-card h3 {
        margin: 0;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.9;
    }
    
    .metric-card .value {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0.5rem 0 0 0;
    }
    
    /* Info Box */
    .info-box {
        background-color: #f8f9fa;
        border-left: 4px solid #2c3e50;
        padding: 1.5rem;
        border-radius: 4px;
        margin: 1.5rem 0;
    }
    
    .info-box h4 {
        margin: 0 0 0.75rem 0;
        color: #2c3e50;
        font-weight: 600;
    }
    
    .info-box ul {
        margin: 0;
        padding-left: 1.25rem;
    }
    
    .info-box li {
        margin: 0.5rem 0;
        color: #495057;
    }
    
    /* Button Styling */
    .stButton > button {
        background-color: #2c3e50;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        letter-spacing: 0.3px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #1a252f;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 2px solid #e0e0e0;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-weight: 500;
        padding: 1rem 0;
    }
    
    /* Remove default Streamlit styling */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    </style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">Crisis Network Analysis System</h1>', unsafe_allow_html=True)
st.markdown('<p class="main-subtitle">Advanced Social Media Analysis Platform for Crisis Response Research</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### CRISIS ANALYSIS PLATFORM")
    st.markdown("---")

    st.markdown("### Navigation")
    st.markdown("""
    **Analysis Modules:**
    - Data Collection: Gather crisis data from social platforms
    - Data Overview: Statistical analysis and patterns
    - Network Analysis: User interaction networks
    - Temporal Analysis: Time-based behavior patterns
    - LIWC Analysis: Cognitive and emotional analysis
    - Report Generation: Export comprehensive reports
    """)

    st.markdown("---")
    st.markdown("### System Status")

    # Check for existing data
    data_dir = project_root / 'data' / 'processed'
    dataset_count = 0
    if data_dir.exists():
        csv_files = list(data_dir.glob('*.csv'))
        dataset_count = len(csv_files)

    # Load main dataset for more detailed stats
    if dataset_count > 0:
        st.metric("Available Datasets", dataset_count)
        
        # Try to load the main LA Wildfires dataset
        main_csv = data_dir / 'la_wildfires_2025_combined.csv'
        if main_csv.exists():
            try:
                import pandas as pd
                df_stats = pd.read_csv(main_csv)
                st.metric("Total Posts Analyzed", f"{len(df_stats):,}")
                
                if 'author' in df_stats.columns:
                    unique_users = df_stats['author'].nunique()
                    st.metric("Unique Users Tracked", f"{unique_users:,}")
                
                # Check for analysis results
                results_dir = project_root / 'results'
                if (results_dir / 'liwc').exists():
                    liwc_files = list((results_dir / 'liwc').glob('liwc_enhanced_*.csv'))
                    if liwc_files:
                        st.success("LIWC Analysis: Complete")
                
                if (results_dir / 'reports').exists():
                    reports = list((results_dir / 'reports').glob('*.html'))
                    if reports:
                        st.metric("Generated Reports", len(reports))
            except Exception as e:
                st.metric("Available Datasets", dataset_count)

    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    **Crisis Network Analysis System**

    Research platform for analyzing social media behavior during crisis events using:
    - Network structure analysis
    - LIWC cognitive framework
    - PADM decision model
    - Temporal pattern detection

    Version 1.0
    """)


# Main content
st.markdown("## Analysis Dashboard Overview")

# Key Findings Section
processed_dir = project_root / 'data' / 'processed'
main_csv = processed_dir / 'la_wildfires_2025_combined.csv'
if main_csv.exists():
    try:
        import pandas as pd
        df_preview = pd.read_csv(main_csv, nrows=5000)
        post_count = len(df_preview)
        user_count = df_preview['author'].nunique() if 'author' in df_preview.columns else 0
        
        # Check for LIWC results
        liwc_dir = project_root / 'results' / 'liwc'
        has_liwc = False
        if liwc_dir.exists():
            liwc_files = list(liwc_dir.glob('liwc_enhanced_*.csv'))
            has_liwc = len(liwc_files) > 0
        
        st.markdown(f"""
        <div class="info-box">
            <h4>Current Analysis: LA Wildfires 2025</h4>
            <ul>
                <li><strong>Posts Analyzed:</strong> {post_count:,}+ from Reddit communities</li>
                <li><strong>Unique Users:</strong> {user_count:,}+ tracked during crisis period</li>
                <li><strong>Crisis Period:</strong> January 7-31, 2025</li>
                <li><strong>Cognitive Analysis:</strong> {'Complete' if has_liwc else 'In Progress'}</li>
                <li><strong>Network Analysis:</strong> User interaction patterns and information hubs identified</li>
                <li><strong>Research Focus:</strong> Information accuracy, evacuation coordination, community resilience</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        pass

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Data Collection")
    st.markdown("""
    Collect crisis-related data from social media platforms.

    Navigate to **Data Collection** module to begin data acquisition.
    """)
    if st.button("Access Data Collection", use_container_width=True):
        st.switch_page("pages/01_Data_Collection.py")

with col2:
    st.markdown("### Analysis Tools")
    st.markdown("""
    Explore collected data and analyze behavioral patterns.

    Navigate to **Data Overview** module for statistical analysis.
    """)
    if st.button("View Analysis Tools", use_container_width=True):
        st.switch_page("pages/02_Data_Overview.py")

with col3:
    st.markdown("### Report Generation")
    st.markdown("""
    Generate comprehensive reports for stakeholders.

    Navigate to **Report Generation** module to create reports.
    """)
    if st.button("Generate Reports", use_container_width=True):
        st.switch_page("pages/06_Generate_Reports.py")

st.markdown("---")

# Quick start guide
st.markdown("## System Guide")

with st.expander("How to use this analysis system", expanded=False):
    st.markdown("""
    ### Step 1: Configure API Keys
    1. Copy `config/api_keys.env.template` to `config/api_keys.env`
    2. Add your Reddit API credentials
    3. Restart the dashboard

    ### Step 2: Collect Data
    1. Navigate to **Data Collection** page
    2. Select a crisis event
    3. Configure collection parameters
    4. Initiate collection process

    ### Step 3: Analyze Data
    1. Navigate to **Data Overview** for dataset statistics
    2. Use **Network Analysis** for user interaction patterns
    3. Check **Temporal Analysis** for time-based patterns
    4. Review **LIWC Analysis** for cognitive insights

    ### Step 4: Generate Reports
    1. Navigate to **Report Generation**
    2. Select your dataset
    3. Choose report type
    4. Export as PDF or HTML
    """)

# System status
st.markdown("---")
st.markdown("## System Status")

col1, col2, col3, col4 = st.columns(4)

with col1:
    # Check if config exists
    config_file = project_root / 'config' / 'api_keys.env'
    if config_file.exists():
        st.success("Configuration: Active")
    else:
        st.warning("Configuration: Required")

with col2:
    # Check for data
    processed_dir = project_root / 'data' / 'processed'
    if processed_dir.exists() and list(processed_dir.glob('*.csv')):
        st.success("Data: Available")
    else:
        st.info("Data: Not Available")

with col3:
    # Check dependencies
    try:
        import pandas
        import networkx
        import plotly
        st.success("Dependencies: Installed")
    except ImportError:
        st.error("Dependencies: Missing")

with col4:
    # Check results directory
    results_dir = project_root / 'results' / 'networks'
    if results_dir.exists() and list(results_dir.glob('*.json')):
        st.success("Results: Generated")
    else:
        st.info("Results: Pending")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>Crisis Network Analysis System v1.0 | Research Platform |
    <a href='https://github.com/411sst/crisis-network-analysis' style='color: #2c3e50;'>GitHub Repository</a></p>
</div>
""", unsafe_allow_html=True)
