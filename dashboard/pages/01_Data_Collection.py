import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
import os

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

st.set_page_config(page_title="Data Collection", page_icon="📥", layout="wide")

st.title("📥 Data Collection Interface")

# Check for API keys
config_file = project_root / 'config' / 'api_keys.env'
if not config_file.exists():
    st.error("⚠️ **API Keys Not Configured!**")
    st.markdown("""
    Please configure your Reddit API credentials:
    1. Copy `config/api_keys.env.template` to `config/api_keys.env`
    2. Add your Reddit credentials
    3. Restart this dashboard

    Get Reddit API credentials at: https://www.reddit.com/prefs/apps
    """)
    st.stop()

# Load environment variables
from dotenv import load_dotenv
load_dotenv(config_file)

# Tabs for different collection methods
tab1, tab2, tab3 = st.tabs(["🔍 Single Crisis", "📚 Batch Collection", "📂 Upload Data"])

with tab1:
    st.markdown("### Collect Data for a Single Crisis")

    col1, col2 = st.columns([1, 1])

    with col1:
        # Crisis selection
        st.markdown("#### Crisis Configuration")

        crisis_event = st.selectbox(
            "Select Crisis Event",
            ["la_wildfires_2025", "turkey_syria_earthquake_2023", "custom"],
            help="Choose a pre-configured crisis or create custom"
        )

        if crisis_event == "custom":
            custom_name = st.text_input("Crisis Name", "my_crisis_event")
            crisis_event = custom_name

        # Collection parameters
        st.markdown("#### Collection Parameters")

        subreddits_input = st.text_area(
            "Subreddits (comma-separated)",
            "LosAngeles, California, wildfire",
            help="Enter subreddit names without 'r/'"
        )
        subreddits = [s.strip() for s in subreddits_input.split(',')]

        search_query = st.text_input(
            "Search Query (optional)",
            "",
            help="Leave empty to collect all posts, or specify keywords"
        )

        limit_per_subreddit = st.number_input(
            "Posts per Subreddit",
            min_value=10,
            max_value=1000,
            value=100,
            step=10,
            help="How many posts to collect from each subreddit"
        )

        time_filter = st.selectbox(
            "Time Filter",
            ["day", "week", "month", "year", "all"],
            index=2,
            help="Time period for collection"
        )

    with col2:
        st.markdown("#### Collection Preview")

        total_estimate = len(subreddits) * limit_per_subreddit

        st.info(f"""
        **Collection Summary:**
        - Crisis: {crisis_event}
        - Subreddits: {len(subreddits)}
        - Posts per subreddit: {limit_per_subreddit}
        - Estimated total: ~{total_estimate} posts
        - Time filter: {time_filter}
        """)

        st.markdown("**Subreddits to collect from:**")
        for sub in subreddits:
            st.markdown(f"- r/{sub}")

    # Collection button
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        collect_button = st.button(
            "🚀 Start Collection",
            type="primary",
            use_container_width=True
        )

    if collect_button:
        # Import collector
        try:
            from collection.working_reddit_collector import WorkingRedditCollector

            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Initialize collector
            status_text.text("Initializing Reddit collector...")

            collector = WorkingRedditCollector(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent=os.getenv('REDDIT_USER_AGENT', 'Crisis Network Analysis v1.0')
            )

            all_posts = []

            # Collect from each subreddit
            for idx, subreddit in enumerate(subreddits):
                status_text.text(f"Collecting from r/{subreddit}... ({idx+1}/{len(subreddits)})")
                progress = (idx) / len(subreddits)
                progress_bar.progress(progress)

                try:
                    if search_query:
                        df = collector.search_posts(
                            subreddit=subreddit,
                            query=search_query,
                            limit=limit_per_subreddit
                        )
                    else:
                        df = collector.collect_posts(
                            subreddit=subreddit,
                            limit=limit_per_subreddit,
                            time_filter=time_filter
                        )

                    if len(df) > 0:
                        df['crisis_id'] = crisis_event
                        df['collection_timestamp'] = datetime.now()
                        all_posts.append(df)

                except Exception as e:
                    st.warning(f"⚠️ Error collecting from r/{subreddit}: {str(e)}")

            progress_bar.progress(1.0)
            status_text.text("Collection complete!")

            # Combine all posts
            if all_posts:
                combined_df = pd.concat(all_posts, ignore_index=True)

                # Save to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{crisis_event}_{timestamp}.csv"

                output_dir = project_root / 'data' / 'raw'
                output_dir.mkdir(parents=True, exist_ok=True)

                output_path = output_dir / filename
                combined_df.to_csv(output_path, index=False)

                st.success(f"""
                ✅ **Collection Successful!**

                - Total posts collected: {len(combined_df)}
                - Unique authors: {combined_df['author'].nunique()}
                - Subreddits: {combined_df['subreddit'].nunique()}
                - Saved to: `{output_path.relative_to(project_root)}`
                """)

                # Show preview
                st.markdown("### 📊 Preview")
                st.dataframe(combined_df.head(10), use_container_width=True)

                # Download button
                csv = combined_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=filename,
                    mime="text/csv",
                    use_container_width=True
                )

            else:
                st.error("❌ No posts collected. Please check your parameters and try again.")

        except ImportError as e:
            st.error(f"❌ Import Error: {e}")
            st.markdown("""
            Please ensure all dependencies are installed:
            ```bash
            pip install -r requirements.txt
            ```
            """)
        except Exception as e:
            st.error(f"❌ Collection Error: {str(e)}")
            st.exception(e)

with tab2:
    st.markdown("### Batch Collection from Multiple Crises")

    st.info("""
    This feature allows you to collect data for multiple crises in one go.

    Coming soon in the next iteration!
    """)

    # Load crisis config
    try:
        import yaml

        config_path = project_root / 'config' / 'crisis_events.yaml'
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            crises = config.get('crisis_events', {})

            st.markdown("**Available Crisis Events:**")

            for crisis_id, details in crises.items():
                with st.expander(f"📌 {details.get('name', crisis_id)}"):
                    st.markdown(f"""
                    - **Type**: {details.get('type', 'N/A')}
                    - **Start**: {details.get('start_date', 'N/A')}
                    - **End**: {details.get('end_date', 'N/A')}
                    - **Subreddits**: {', '.join(details.get('platforms', {}).get('reddit', {}).get('subreddits', []))}
                    """)

    except Exception as e:
        st.warning(f"Could not load crisis configuration: {e}")

with tab3:
    st.markdown("### Upload Existing Dataset")

    st.markdown("""
    If you already have collected data, you can upload it here.

    **Supported formats**: CSV files with Reddit post data
    """)

    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload a CSV file containing Reddit posts"
    )

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)

            st.success(f"✅ File uploaded successfully! ({len(df)} rows)")

            st.markdown("### 📊 Dataset Preview")
            st.dataframe(df.head(20), use_container_width=True)

            st.markdown("### 📈 Quick Stats")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Posts", len(df))

            with col2:
                if 'author' in df.columns:
                    st.metric("Unique Authors", df['author'].nunique())

            with col3:
                if 'subreddit' in df.columns:
                    st.metric("Subreddits", df['subreddit'].nunique())

            with col4:
                if 'score' in df.columns:
                    st.metric("Avg Score", f"{df['score'].mean():.1f}")

            # Save option
            st.markdown("---")

            crisis_name = st.text_input(
                "Crisis Name (for saving)",
                "uploaded_data",
                key="upload_crisis_name"
            )

            if st.button("💾 Save to Data Directory", use_container_width=True):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{crisis_name}_{timestamp}.csv"

                output_dir = project_root / 'data' / 'raw'
                output_dir.mkdir(parents=True, exist_ok=True)

                output_path = output_dir / filename
                df.to_csv(output_path, index=False)

                st.success(f"✅ Saved to: `{output_path.relative_to(project_root)}`")

        except Exception as e:
            st.error(f"❌ Error processing file: {e}")

# Footer with helpful links
st.markdown("---")
st.markdown("""
### 💡 Tips for Data Collection

1. **Start Small**: Test with 50-100 posts per subreddit first
2. **Rate Limits**: Reddit API has rate limits - be patient with large collections
3. **Time Filters**: Use 'week' or 'month' for recent crises, 'all' for historical
4. **Search Queries**: Use specific keywords for better relevance
5. **Save Often**: Download your data immediately after collection

### 📚 Resources

- [Reddit API Documentation](https://www.reddit.com/dev/api)
- [PRAW Documentation](https://praw.readthedocs.io/)
- [Project Documentation](../docs/api_reference.md)
""")
