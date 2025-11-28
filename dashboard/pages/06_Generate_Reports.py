import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path
from datetime import datetime
import base64

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

st.set_page_config(page_title="Generate Reports", page_icon="📄", layout="wide")

st.title("📄 Generate Reports")

st.markdown("""
Create professional PDF or HTML reports from your crisis data analysis.
""")

# Find datasets
data_dir = project_root / 'data'
raw_dir = data_dir / 'raw'
processed_dir = data_dir / 'processed'

csv_files = []
if raw_dir.exists():
    csv_files.extend([(f, 'raw') for f in raw_dir.glob('*.csv')])
if processed_dir.exists():
    csv_files.extend([(f, 'processed') for f in processed_dir.glob('*.csv')])

if not csv_files:
    st.warning("⚠️ No datasets found! Please collect or upload data first.")
    st.stop()

# Report configuration
st.markdown("## ⚙️ Report Configuration")

col1, col2 = st.columns([2, 1])

with col1:
    # Select dataset
    file_options = {f"{f.name} ({source})": (f, source) for f, source in csv_files}
    selected_file_name = st.selectbox(
        "Select Dataset",
        options=list(file_options.keys())
    )
    selected_file, source = file_options[selected_file_name]

    # Report type
    report_type = st.selectbox(
        "Report Type",
        ["Executive Summary", "Comprehensive Analysis", "Quick Stats"],
        help="Choose the type of report to generate"
    )

    # Report title
    report_title = st.text_input(
        "Report Title",
        f"Crisis Network Analysis Report - {datetime.now().strftime('%Y-%m-%d')}"
    )

with col2:
    # Export format
    export_format = st.radio(
        "Export Format",
        ["📄 PDF", "🌐 HTML", "📊 Both"]
    )

    # Include sections
    st.markdown("**Include Sections:**")
    include_overview = st.checkbox("Overview & Stats", value=True)
    include_temporal = st.checkbox("Temporal Analysis", value=True)
    include_authors = st.checkbox("Author Analysis", value=True)
    include_quality = st.checkbox("Quality Metrics", value=True)

# Load data
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    # Convert timestamps
    for col in ['created_utc', 'timestamp']:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                pass
    return df

try:
    df = load_data(selected_file)
    st.success(f"✅ Data loaded: {len(df):,} posts")
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

st.markdown("---")

# Generate report button
if st.button("🚀 Generate Report", type="primary", use_container_width=True):
    with st.spinner("Generating report..."):

        # Create HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{report_title}</title>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .header {{
                    background: linear-gradient(135deg, #1f77b4 0%, #2ca02c 100%);
                    color: white;
                    padding: 40px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 2.5em;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    font-size: 1.2em;
                    opacity: 0.9;
                }}
                .section {{
                    background: white;
                    padding: 30px;
                    margin-bottom: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .section h2 {{
                    color: #1f77b4;
                    border-bottom: 3px solid #1f77b4;
                    padding-bottom: 10px;
                    margin-top: 0;
                }}
                .metric-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }}
                .metric-card {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 4px solid #1f77b4;
                }}
                .metric-card h3 {{
                    margin: 0;
                    color: #666;
                    font-size: 0.9em;
                    font-weight: normal;
                }}
                .metric-card .value {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #1f77b4;
                    margin: 10px 0;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #1f77b4;
                    color: white;
                    font-weight: bold;
                }}
                tr:hover {{
                    background-color: #f5f5f5;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #666;
                    font-size: 0.9em;
                }}
                .chart-container {{
                    margin: 20px 0;
                    padding: 20px;
                    background: #fafafa;
                    border-radius: 8px;
                }}
                @media print {{
                    body {{
                        background-color: white;
                    }}
                    .section {{
                        page-break-inside: avoid;
                        box-shadow: none;
                        border: 1px solid #ddd;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{report_title}</h1>
                <p>Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
                <p>Dataset: {selected_file.name}</p>
            </div>
        """

        # Overview Section
        if include_overview:
            html_content += f"""
            <div class="section">
                <h2>📊 Executive Summary</h2>
                <div class="metric-grid">
                    <div class="metric-card">
                        <h3>Total Posts</h3>
                        <div class="value">{len(df):,}</div>
                    </div>
                    <div class="metric-card">
                        <h3>Unique Authors</h3>
                        <div class="value">{df['author'].nunique() if 'author' in df.columns else 'N/A'}</div>
                    </div>
                    <div class="metric-card">
                        <h3>Subreddits</h3>
                        <div class="value">{df['subreddit'].nunique() if 'subreddit' in df.columns else 'N/A'}</div>
                    </div>
                    <div class="metric-card">
                        <h3>Average Score</h3>
                        <div class="value">{df['score'].mean():.1f if 'score' in df.columns else 'N/A'}</div>
                    </div>
                    <div class="metric-card">
                        <h3>Total Comments</h3>
                        <div class="value">{df['num_comments'].sum():,} if 'num_comments' in df.columns else 'N/A'}</div>
                    </div>
                    <div class="metric-card">
                        <h3>Avg Engagement</h3>
                        <div class="value">{df['num_comments'].mean():.1f} if 'num_comments' in df.columns else 'N/A'}</div>
                    </div>
                </div>

                <h3>Key Findings</h3>
                <ul>
                    <li>Dataset contains <strong>{len(df):,} posts</strong> from <strong>{df['subreddit'].nunique() if 'subreddit' in df.columns else 'N/A'} subreddits</strong></li>
                    <li>Contributed by <strong>{df['author'].nunique() if 'author' in df.columns else 'N/A'} unique authors</strong></li>
                    <li>Average post score: <strong>{df['score'].mean():.1f}</strong> points</li>
                    <li>Average comments per post: <strong>{df['num_comments'].mean():.1f if 'num_comments' in df.columns else 'N/A'}</strong></li>
            """

            # Add date range if available
            timestamp_col = None
            for col in ['created_utc', 'timestamp']:
                if col in df.columns:
                    timestamp_col = col
                    break

            if timestamp_col:
                df[timestamp_col] = pd.to_datetime(df[timestamp_col])
                min_date = df[timestamp_col].min()
                max_date = df[timestamp_col].max()
                html_content += f"""
                    <li>Date range: <strong>{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}</strong></li>
                    <li>Duration: <strong>{(max_date - min_date).days} days</strong></li>
                """

            html_content += """
                </ul>
            </div>
            """

        # Temporal Analysis
        if include_temporal and timestamp_col:
            html_content += """
            <div class="section">
                <h2>📅 Temporal Analysis</h2>
                <p>Analysis of posting patterns over time.</p>

                <h3>Posting Activity Timeline</h3>
            """

            # Create posts per day chart
            df['date'] = df[timestamp_col].dt.date
            posts_per_day = df.groupby('date').size().reset_index(name='posts')

            fig = px.line(posts_per_day, x='date', y='posts', title='Posts Over Time')
            chart_html = fig.to_html(include_plotlyjs='cdn', div_id='timeline_chart')
            html_content += f'<div class="chart-container">{chart_html}</div>'

            # Hour analysis
            df['hour'] = df[timestamp_col].dt.hour
            posts_per_hour = df.groupby('hour').size().reset_index(name='posts')
            peak_hour = posts_per_hour.loc[posts_per_hour['posts'].idxmax(), 'hour']

            html_content += f"""
                <h3>Peak Activity Hours</h3>
                <p>Most active posting hour: <strong>{int(peak_hour)}:00</strong></p>
            """

            fig = px.bar(posts_per_hour, x='hour', y='posts', title='Posts by Hour of Day')
            chart_html = fig.to_html(include_plotlyjs='cdn', div_id='hour_chart')
            html_content += f'<div class="chart-container">{chart_html}</div>'

            html_content += "</div>"

        # Author Analysis
        if include_authors and 'author' in df.columns:
            html_content += """
            <div class="section">
                <h2>👥 Author Analysis</h2>
            """

            top_authors = df['author'].value_counts().head(10).reset_index()
            top_authors.columns = ['Author', 'Posts']

            html_content += "<h3>Top 10 Most Active Authors</h3><table><tr><th>Rank</th><th>Author</th><th>Posts</th><th>% of Total</th></tr>"

            for idx, row in top_authors.iterrows():
                pct = (row['Posts'] / len(df)) * 100
                html_content += f"<tr><td>{idx+1}</td><td>{row['Author']}</td><td>{row['Posts']}</td><td>{pct:.2f}%</td></tr>"

            html_content += "</table></div>"

        # Subreddit Analysis
        if 'subreddit' in df.columns:
            html_content += """
            <div class="section">
                <h2>📌 Subreddit Distribution</h2>
            """

            subreddit_counts = df['subreddit'].value_counts().reset_index()
            subreddit_counts.columns = ['Subreddit', 'Posts']

            html_content += "<table><tr><th>Subreddit</th><th>Posts</th><th>% of Total</th></tr>"

            for idx, row in subreddit_counts.iterrows():
                pct = (row['Posts'] / len(df)) * 100
                html_content += f"<tr><td>r/{row['Subreddit']}</td><td>{row['Posts']}</td><td>{pct:.2f}%</td></tr>"

            html_content += "</table></div>"

        # Quality Metrics
        if include_quality:
            try:
                from preprocessing.quality_validator import QualityValidator

                validator = QualityValidator()
                results = validator.validate_dataset(df)

                html_content += f"""
                <div class="section">
                    <h2>✅ Data Quality Assessment</h2>
                    <div class="metric-grid">
                        <div class="metric-card">
                            <h3>Overall Quality</h3>
                            <div class="value">{results['overall_score']:.1f}/100</div>
                        </div>
                        <div class="metric-card">
                            <h3>Completeness</h3>
                            <div class="value">{results['completeness']['score']:.1f}/100</div>
                        </div>
                        <div class="metric-card">
                            <h3>Consistency</h3>
                            <div class="value">{results['consistency']['score']:.1f}/100</div>
                        </div>
                        <div class="metric-card">
                            <h3>Content Quality</h3>
                            <div class="value">{results['content_quality']['quality_score']:.1f}/100</div>
                        </div>
                    </div>

                    <h3>Quality Notes</h3>
                    <ul>
                        <li>Completeness Score: {results['completeness']['score']:.1f}% - Measures data completeness</li>
                        <li>Consistency Score: {results['consistency']['score']:.1f}% - Checks for data inconsistencies</li>
                        <li>Content Quality: {results['content_quality']['quality_score']:.1f}% - Evaluates content quality</li>
                        <li>Issues Found: {results['consistency']['timestamp_issues'] + results['consistency']['negative_scores']} total issues</li>
                    </ul>
                </div>
                """
            except Exception as e:
                st.warning(f"Could not generate quality metrics: {e}")

        # Methodology section
        html_content += """
        <div class="section">
            <h2>📚 Methodology</h2>
            <h3>Data Collection</h3>
            <p>Data was collected using the Reddit API (PRAW) following ethical research guidelines.</p>

            <h3>Analysis Framework</h3>
            <ul>
                <li><strong>Network Analysis</strong>: Using NetworkX for graph analysis</li>
                <li><strong>LIWC Integration</strong>: Linguistic Inquiry and Word Count for cognitive analysis</li>
                <li><strong>PADM Framework</strong>: Protective Action Decision Model for crisis behavior</li>
                <li><strong>Statistical Analysis</strong>: Pandas and NumPy for data processing</li>
            </ul>

            <h3>Quality Assurance</h3>
            <p>All data undergoes automated quality validation including completeness checks,
            consistency validation, and content quality assessment.</p>
        </div>
        """

        # Footer
        html_content += f"""
        <div class="footer">
            <p><strong>Crisis Network Analysis Dashboard</strong></p>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Dataset: {selected_file.name} | Total Posts: {len(df):,}</p>
            <p>For questions or more information, visit the project repository</p>
        </div>
        </body>
        </html>
        """

        # Save HTML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = project_root / 'results' / 'reports'
        output_dir.mkdir(parents=True, exist_ok=True)

        html_path = output_dir / f"report_{timestamp}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        st.success(f"✅ Report generated successfully!")

        # Display HTML
        st.markdown("## 📄 Report Preview")
        st.components.v1.html(html_content, height=600, scrolling=True)

        # Download buttons
        col1, col2 = st.columns(2)

        with col1:
            # HTML download
            st.download_button(
                label="📥 Download HTML Report",
                data=html_content,
                file_name=f"crisis_report_{timestamp}.html",
                mime="text/html",
                use_container_width=True
            )

        with col2:
            # PDF generation note
            st.info("""
            **PDF Generation:**

            To convert to PDF, open the HTML file in your browser and use "Print to PDF" (Ctrl+P / Cmd+P)

            Or install WeasyPrint:
            ```bash
            pip install weasyprint
            ```
            Then use the Python API to generate PDF programmatically.
            """)

        # Show file path
        st.success(f"Report saved to: `{html_path.relative_to(project_root)}`")

# Quick export section
st.markdown("---")
st.markdown("## 📊 Quick Export Options")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📥 Export Data to CSV", use_container_width=True):
        csv = df.to_csv(index=False)
        st.download_button(
            "Download CSV",
            data=csv,
            file_name=f"data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

with col2:
    if st.button("📊 Export Statistics to JSON", use_container_width=True):
        stats = {
            'total_posts': len(df),
            'unique_authors': int(df['author'].nunique()) if 'author' in df.columns else None,
            'unique_subreddits': int(df['subreddit'].nunique()) if 'subreddit' in df.columns else None,
            'avg_score': float(df['score'].mean()) if 'score' in df.columns else None,
            'avg_comments': float(df['num_comments'].mean()) if 'num_comments' in df.columns else None,
            'generated': datetime.now().isoformat()
        }

        import json
        stats_json = json.dumps(stats, indent=2)

        st.download_button(
            "Download JSON",
            data=stats_json,
            file_name=f"stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

with col3:
    st.info("""
    **More Export Options:**
    - Network graphs: See Network Analysis page
    - LIWC results: See LIWC Analysis page
    """)
