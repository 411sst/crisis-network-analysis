# Crisis Network Analysis Dashboard

Interactive web dashboard for crisis social media analysis.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r ../requirements.txt
```

### 2. Configure API Keys

```bash
cp ../config/api_keys.env.template ../config/api_keys.env
# Edit config/api_keys.env with your Reddit credentials
```

### 3. Run the Dashboard

**Option A: Using the launcher script**
```bash
python ../run_dashboard.py
```

**Option B: Direct Streamlit command**
```bash
streamlit run app.py
```

The dashboard will open at: http://localhost:8501

## 📊 Dashboard Pages

### 1. **Home** (`app.py`)
- Quick start guide
- System status check
- Navigation overview

### 2. **Data Collection** (`pages/01_Data_Collection.py`)
- Collect Reddit data
- Configure crisis parameters
- Upload existing datasets
- Real-time progress tracking

### 3. **Data Overview** (`pages/02_Data_Overview.py`)
- Dataset statistics
- Data quality validation
- Distribution analysis
- Author and subreddit insights
- Temporal patterns

### 4. **Network Analysis** (`pages/03_Network_Analysis.py`)
- Interactive network visualization
- Hub identification
- Centrality metrics
- Community detection
- Export network data

### 5. **LIWC Analysis** (`pages/05_LIWC_Analysis.py`)
- Cognitive process analysis
- Emotional patterns
- PADM framework integration
- Temporal evolution of sentiment

### 6. **Generate Reports** (`pages/06_Generate_Reports.py`)
- Executive summary reports
- Comprehensive analysis reports
- PDF and HTML export
- Customizable sections

## 🎯 Features

### Data Collection
- ✅ Reddit API integration
- ✅ Multiple subreddit support
- ✅ Keyword search
- ✅ Batch collection
- ✅ Data upload

### Analysis
- ✅ Quality validation (automated scoring)
- ✅ Network graph visualization (interactive)
- ✅ Hub classification (6 types)
- ✅ LIWC cognitive analysis
- ✅ Temporal pattern analysis
- ✅ Cross-crisis comparison

### Visualization
- ✅ Interactive Plotly charts
- ✅ Network graphs with zoom/pan
- ✅ Time series analysis
- ✅ Distribution plots
- ✅ Correlation matrices
- ✅ Geographic maps (if data available)

### Export
- ✅ CSV data export
- ✅ HTML reports
- ✅ PDF reports (via browser print)
- ✅ Network files (GraphML)
- ✅ JSON statistics

## 🛠️ Configuration

### Environment Variables

Required (in `config/api_keys.env`):
```bash
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=Crisis Network Analysis v1.0
```

### Dashboard Settings

Modify `.streamlit/config.toml` (create if needed):
```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[server]
port = 8501
headless = false
enableCORS = false
```

## 📂 Project Structure

```
dashboard/
├── app.py                    # Main dashboard
├── pages/                    # Multi-page app
│   ├── 01_Data_Collection.py
│   ├── 02_Data_Overview.py
│   ├── 03_Network_Analysis.py
│   ├── 05_LIWC_Analysis.py
│   └── 06_Generate_Reports.py
├── components/               # Reusable components (future)
├── utils/                    # Utility functions (future)
└── README.md                 # This file
```

## 💡 Usage Tips

### Data Collection
1. Start with small batches (50-100 posts) to test
2. Use specific search queries for better relevance
3. Check rate limits - Reddit allows ~60 requests/minute
4. Save data frequently

### Analysis
1. Run quality validation before analysis
2. Export data at each stage
3. Use filters to focus on specific patterns
4. Compare multiple datasets side-by-side

### Reports
1. Generate reports after completing analysis
2. Include all relevant sections
3. Download HTML for sharing
4. Use browser "Print to PDF" for PDF export

## 🐛 Troubleshooting

### Dashboard won't start
```bash
# Check Streamlit installation
streamlit --version

# Reinstall if needed
pip install --upgrade streamlit
```

### Import errors
```bash
# Ensure all dependencies installed
pip install -r ../requirements.txt

# Check Python path
echo $PYTHONPATH
```

### API errors
```bash
# Verify credentials in config/api_keys.env
# Test Reddit connection:
python -c "import praw; print(praw.__version__)"
```

### No data showing
- Check if CSV files exist in `data/raw/` or `data/processed/`
- Verify file permissions
- Try uploading a test file

### Slow performance
- Large datasets (>10,000 posts) may be slow
- Use filters to reduce dataset size
- Enable caching (default in Streamlit)
- Consider processing data offline first

## 🔧 Advanced Features (Coming Soon)

- [ ] Real-time data collection
- [ ] PostgreSQL database integration
- [ ] Advanced filtering options
- [ ] Custom report templates
- [ ] Automated scheduling
- [ ] User authentication
- [ ] Multi-user support
- [ ] Cloud deployment

## 📝 Development

### Adding New Pages

1. Create file in `pages/` with format `##_Page_Name.py`
2. Use page config:
```python
import streamlit as st
st.set_page_config(page_title="My Page", page_icon="🎯", layout="wide")
```

3. Streamlit will auto-detect and add to sidebar

### Custom Components

Create reusable components in `components/`:
```python
# components/my_component.py
import streamlit as st

def my_component(data):
    st.write("Custom component")
    return data
```

## 📚 Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Documentation](https://plotly.com/python/)
- [Project Documentation](../docs/)
- [PRAW Documentation](https://praw.readthedocs.io/)

## 🤝 Contributing

See main [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## 📄 License

See [LICENSE](../LICENSE) for details.

---

**Need help?** Open an issue or check the documentation!
