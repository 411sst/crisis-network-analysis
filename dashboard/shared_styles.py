"""
Shared professional styling for Crisis Network Analysis System
"""

PROFESSIONAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global Styling */
* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

h1, h2, h3, h4, h5, h6 {
    font-weight: 600;
    color: #1a1a2e;
    letter-spacing: -0.3px;
}

/* Page Title */
.page-title {
    font-size: 2.2rem;
    font-weight: 600;
    color: #1a1a2e;
    padding: 1.5rem 0 1rem 0;
    border-bottom: 2px solid #e0e0e0;
    margin-bottom: 1.5rem;
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
    border-radius: 4px;
}

.stButton > button:hover {
    background-color: #1a252f;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.stButton > button[kind="primary"] {
    background-color: #667eea;
}

.stButton > button[kind="primary"]:hover {
    background-color: #5568d3;
}

/* Metric Cards */
[data-testid="stMetric"] {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 4px;
    border-left: 3px solid #2c3e50;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 1.5rem;
    border-bottom: 2px solid #e0e0e0;
}

.stTabs [data-baseweb="tab"] {
    font-weight: 500;
    padding: 0.75rem 0;
    color: #495057;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #2c3e50;
}

/* Info boxes */
.stAlert {
    border-radius: 4px;
    border-left-width: 4px;
}

/* Tables */
.dataframe {
    font-size: 0.9rem;
}

.dataframe th {
    background-color: #2c3e50 !important;
    color: white !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    font-size: 0.8rem;
    letter-spacing: 0.5px;
}

/* Expander */
.streamlit-expanderHeader {
    font-weight: 500;
    color: #2c3e50;
}

/* Remove Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}

/* Select boxes and inputs */
.stSelectbox label, .stTextInput label, .stNumberInput label, .stTextArea label {
    font-weight: 500;
    color: #2c3e50;
    font-size: 0.9rem;
}

/* Download buttons */
.stDownloadButton > button {
    background-color: #28a745;
}

.stDownloadButton > button:hover {
    background-color: #218838;
}

</style>
"""
