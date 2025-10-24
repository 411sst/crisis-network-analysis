import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

st.set_page_config(page_title="Data Overview", page_icon="📊", layout="wide")

st.title("📊 Data Overview & Analysis")

# File selector
data_dir = project_root / 'data'
raw_dir = data_dir / 'raw'
processed_dir = data_dir / 'processed'

# Find all CSV files
csv_files = []
if raw_dir.exists():
    csv_files.extend([(f, 'raw') for f in raw_dir.glob('*.csv')])
if processed_dir.exists():
    csv_files.extend([(f, 'processed') for f in processed_dir.glob('*.csv')])

if not csv_files:
    st.warning("⚠️ No datasets found!")
    st.markdown("""
    **Get started:**
    1. Go to the **Data Collection** page to collect new data
    2. Or upload an existing CSV file
    3. Or check if files exist in `data/raw/` or `data/processed/`
    """)
    st.stop()

# Create file selection
file_options = {f"{f.name} ({source})": (f, source) for f, source in csv_files}
selected_file_name = st.selectbox(
    "Select Dataset",
    options=list(file_options.keys()),
    help="Choose a dataset to analyze"
)

selected_file, source = file_options[selected_file_name]

# Load data
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)

    # Convert timestamps if they exist
    timestamp_cols = ['created_utc', 'timestamp', 'collection_timestamp']
    for col in timestamp_cols:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                pass

    return df

try:
    df = load_data(selected_file)

    st.success(f"✅ Loaded: **{selected_file.name}** ({len(df):,} posts)")

except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

# Overview metrics
st.markdown("## 📈 Dataset Summary")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Posts", f"{len(df):,}")

with col2:
    if 'author' in df.columns:
        unique_authors = df['author'].nunique()
        st.metric("Unique Authors", f"{unique_authors:,}")

with col3:
    if 'subreddit' in df.columns:
        unique_subs = df['subreddit'].nunique()
        st.metric("Subreddits", f"{unique_subs:,}")

with col4:
    if 'score' in df.columns:
        avg_score = df['score'].mean()
        st.metric("Avg Score", f"{avg_score:.1f}")

with col5:
    if 'num_comments' in df.columns:
        avg_comments = df['num_comments'].mean()
        st.metric("Avg Comments", f"{avg_comments:.1f}")

# Tabs for different views
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Data Table",
    "📊 Distributions",
    "📅 Temporal Analysis",
    "👥 Authors & Subreddits",
    "🔍 Quality Check"
])

with tab1:
    st.markdown("### Dataset Preview")

    # Filters
    col1, col2 = st.columns([3, 1])

    with col1:
        search_term = st.text_input("🔍 Search in titles/content", "")

    with col2:
        show_rows = st.number_input("Rows to display", 10, 1000, 50)

    # Apply filters
    filtered_df = df.copy()

    if search_term:
        if 'title' in df.columns and 'content' in df.columns:
            filtered_df = df[
                df['title'].str.contains(search_term, case=False, na=False) |
                df['content'].str.contains(search_term, case=False, na=False)
            ]
        elif 'title' in df.columns:
            filtered_df = df[df['title'].str.contains(search_term, case=False, na=False)]

    st.markdown(f"**Showing {min(show_rows, len(filtered_df))} of {len(filtered_df)} posts**")

    # Display columns selector
    if len(df.columns) > 10:
        display_cols = st.multiselect(
            "Select columns to display",
            options=df.columns.tolist(),
            default=['title', 'author', 'subreddit', 'score', 'num_comments'][:len(df.columns)]
        )
    else:
        display_cols = df.columns.tolist()

    st.dataframe(
        filtered_df[display_cols].head(show_rows),
        use_container_width=True,
        height=400
    )

    # Download filtered data
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        "📥 Download Filtered Data",
        data=csv,
        file_name=f"filtered_{selected_file.name}",
        mime="text/csv"
    )

with tab2:
    st.markdown("### Data Distributions")

    col1, col2 = st.columns(2)

    with col1:
        # Score distribution
        if 'score' in df.columns:
            fig = px.histogram(
                df,
                x='score',
                nbins=50,
                title="Post Score Distribution",
                labels={'score': 'Score', 'count': 'Number of Posts'}
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Comment distribution
        if 'num_comments' in df.columns:
            fig = px.histogram(
                df,
                x='num_comments',
                nbins=50,
                title="Comments Distribution",
                labels={'num_comments': 'Number of Comments', 'count': 'Number of Posts'}
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        # Upvote ratio distribution
        if 'upvote_ratio' in df.columns:
            fig = px.histogram(
                df,
                x='upvote_ratio',
                nbins=30,
                title="Upvote Ratio Distribution",
                labels={'upvote_ratio': 'Upvote Ratio', 'count': 'Number of Posts'}
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Content length distribution (if we can calculate it)
        if 'content' in df.columns:
            df['content_length'] = df['content'].str.len()
            fig = px.histogram(
                df,
                x='content_length',
                nbins=50,
                title="Content Length Distribution",
                labels={'content_length': 'Content Length (characters)', 'count': 'Number of Posts'}
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("### Temporal Analysis")

    timestamp_col = None
    for col in ['created_utc', 'timestamp', 'collection_timestamp']:
        if col in df.columns:
            timestamp_col = col
            break

    if timestamp_col:
        # Ensure datetime
        df[timestamp_col] = pd.to_datetime(df[timestamp_col])

        # Posts over time
        df['date'] = df[timestamp_col].dt.date
        posts_per_day = df.groupby('date').size().reset_index(name='posts')

        fig = px.line(
            posts_per_day,
            x='date',
            y='posts',
            title="Posts Over Time",
            labels={'date': 'Date', 'posts': 'Number of Posts'}
        )
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            # Posts by hour
            df['hour'] = df[timestamp_col].dt.hour
            posts_per_hour = df.groupby('hour').size().reset_index(name='posts')

            fig = px.bar(
                posts_per_hour,
                x='hour',
                y='posts',
                title="Posts by Hour of Day",
                labels={'hour': 'Hour (24h)', 'posts': 'Number of Posts'}
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Posts by day of week
            df['day_of_week'] = df[timestamp_col].dt.day_name()
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            posts_per_dow = df.groupby('day_of_week').size().reindex(day_order).reset_index(name='posts')

            fig = px.bar(
                posts_per_dow,
                x='day_of_week',
                y='posts',
                title="Posts by Day of Week",
                labels={'day_of_week': 'Day', 'posts': 'Number of Posts'}
            )
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("⚠️ No timestamp column found in the dataset")

with tab4:
    st.markdown("### Authors & Subreddits Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Top authors
        if 'author' in df.columns:
            st.markdown("#### 👥 Top 10 Authors")
            top_authors = df['author'].value_counts().head(10).reset_index()
            top_authors.columns = ['Author', 'Posts']

            fig = px.bar(
                top_authors,
                x='Posts',
                y='Author',
                orientation='h',
                title="Top 10 Most Active Authors"
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

            # Show table
            st.dataframe(top_authors, use_container_width=True)

    with col2:
        # Top subreddits
        if 'subreddit' in df.columns:
            st.markdown("#### 📌 Subreddits")
            subreddit_counts = df['subreddit'].value_counts().reset_index()
            subreddit_counts.columns = ['Subreddit', 'Posts']

            fig = px.pie(
                subreddit_counts,
                values='Posts',
                names='Subreddit',
                title="Posts by Subreddit"
            )
            st.plotly_chart(fig, use_container_width=True)

            # Show table
            st.dataframe(subreddit_counts, use_container_width=True)

    # Author engagement metrics
    if 'author' in df.columns and 'score' in df.columns:
        st.markdown("#### 🏆 Top Authors by Engagement")

        author_stats = df.groupby('author').agg({
            'score': ['sum', 'mean'],
            'num_comments': ['sum', 'mean'] if 'num_comments' in df.columns else 'count',
            'title': 'count'
        }).reset_index()

        author_stats.columns = ['Author', 'Total Score', 'Avg Score', 'Total Comments', 'Avg Comments', 'Posts']
        author_stats = author_stats.sort_values('Total Score', ascending=False).head(10)

        st.dataframe(author_stats, use_container_width=True)

with tab5:
    st.markdown("### Quality Check")

    # Import quality validator
    try:
        from preprocessing.quality_validator import QualityValidator

        validator = QualityValidator()

        with st.spinner("Running quality validation..."):
            results = validator.validate_dataset(df)

        # Overall score
        st.markdown("## 🎯 Overall Quality Score")

        score = results['overall_score']
        if score >= 90:
            color = "green"
            label = "EXCELLENT"
        elif score >= 75:
            color = "blue"
            label = "GOOD"
        elif score >= 60:
            color = "orange"
            label = "ACCEPTABLE"
        else:
            color = "red"
            label = "NEEDS IMPROVEMENT"

        st.markdown(f"""
        <div style='text-align: center; padding: 2rem; background-color: #f0f2f6; border-radius: 10px;'>
            <h1 style='color: {color}; font-size: 4rem; margin: 0;'>{score:.1f}/100</h1>
            <h3 style='color: {color}; margin: 0;'>{label}</h3>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Detailed metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### 📋 Completeness")
            comp_score = results['completeness']['score']
            st.metric("Score", f"{comp_score:.1f}/100")

            st.markdown("**Column Completeness:**")
            for col, pct in results['completeness']['column_completeness'].items():
                st.progress(pct/100, text=f"{col}: {pct:.1f}%")

        with col2:
            st.markdown("### ✅ Consistency")
            cons_score = results['consistency']['score']
            st.metric("Score", f"{cons_score:.1f}/100")

            st.markdown("**Issues Found:**")
            st.markdown(f"- Timestamp issues: {results['consistency']['timestamp_issues']}")
            st.markdown(f"- Negative scores: {results['consistency']['negative_scores']}")
            st.markdown(f"- Invalid ratios: {results['consistency']['invalid_ratios']}")
            st.markdown(f"- Empty content: {results['consistency']['empty_content']}")

        with col3:
            st.markdown("### 📝 Content Quality")
            qual_score = results['content_quality']['quality_score']
            st.metric("Score", f"{qual_score:.1f}/100")

            st.markdown("**Metrics:**")
            st.markdown(f"- Avg content length: {results['content_quality']['avg_content_length']:.0f}")
            st.markdown(f"- Too short: {results['content_quality']['too_short_count']}")
            st.markdown(f"- Spam indicators: {results['content_quality']['spam_indicators']}")

        # Full report
        with st.expander("📄 View Full Quality Report"):
            report = validator.generate_quality_report()
            st.text(report)

    except ImportError:
        st.warning("⚠️ Quality validator not available. Please check if preprocessing modules are installed.")
    except Exception as e:
        st.error(f"❌ Error running quality check: {e}")

# Footer
st.markdown("---")
st.markdown("""
💡 **Tip**: Use the filters and tabs above to explore your data from different angles.
For detailed analysis, check out the Network Analysis and LIWC Analysis pages.
""")
