import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

st.set_page_config(page_title="LIWC Analysis", page_icon="🧠", layout="wide")

st.title("🧠 LIWC Cognitive & Emotional Analysis")

st.markdown("""
Analyze cognitive and emotional processes using the LIWC framework integrated with PADM (Protective Action Decision Model).
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
    st.warning("⚠️ No datasets found!")
    st.stop()

# Dataset selector
file_options = {f"{f.name} ({source})": (f, source) for f, source in csv_files}
selected_file_name = st.selectbox("Select Dataset", options=list(file_options.keys()))
selected_file, source = file_options[selected_file_name]

# Load data
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    return df

df = load_data(selected_file)

st.success(f"✅ Loaded {len(df):,} posts")

# Check if LIWC scores exist
has_liwc_scores = any(col in df.columns for col in ['cogproc', 'affect', 'social', 'risk'])

if not has_liwc_scores:
    # Try to load existing LIWC results
    results_dir = project_root / 'results' / 'liwc'
    liwc_datasets = list(results_dir.glob('liwc_enhanced_dataset_*.csv')) if results_dir.exists() else []
    
    if liwc_datasets:
        # Use the most recent LIWC-enhanced dataset
        latest_liwc = sorted(liwc_datasets)[-1]
        st.info(f"📊 Loading pre-computed LIWC results from: `{latest_liwc.name}`")
        df = pd.read_csv(latest_liwc)
        has_liwc_scores = True
    else:
        st.warning("""
        ⚠️ **LIWC scores not found in dataset!**

        This dataset hasn't been processed with LIWC yet.

        To run LIWC analysis, use the LIWC integration module:
        ```python
        python scripts/run_liwc_integration.py
        ```

        For now, we'll show mock data visualization examples.
        """)

        # Create mock LIWC scores for demonstration
        import numpy as np

        np.random.seed(42)
        df['cogproc'] = np.random.uniform(5, 15, len(df))
        df['affect'] = np.random.uniform(3, 12, len(df))
        df['social'] = np.random.uniform(8, 18, len(df))
        df['risk'] = np.random.uniform(1, 8, len(df))
        df['certainty'] = np.random.uniform(2, 10, len(df))
        df['tentative'] = np.random.uniform(1, 7, len(df))
        df['posemo'] = np.random.uniform(2, 10, len(df))
        df['negemo'] = np.random.uniform(3, 12, len(df))

        st.info("📊 **Showing example visualizations with mock data**")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🧠 Cognitive Processes",
    "❤️ Emotional Processes",
    "📊 PADM Analysis",
    "📈 Temporal Patterns"
])

with tab1:
    st.markdown("### Cognitive Processes Analysis")

    st.markdown("""
    **LIWC Cognitive Categories:**
    - **Cogproc**: Cognitive processes (think, know, consider)
    - **Certainty**: Certainty and confidence (sure, certain, definitely)
    - **Tentative**: Tentative language (maybe, perhaps, might)
    - **Causation**: Causal thinking (because, cause, due)
    """)

    # Overall statistics
    cognitive_cols = ['cogproc', 'certainty', 'tentative']
    cognitive_cols = [c for c in cognitive_cols if c in df.columns]

    if cognitive_cols:
        col1, col2, col3 = st.columns(3)

        with col1:
            if 'cogproc' in df.columns:
                avg_cogproc = df['cogproc'].mean()
                st.metric("Avg Cognitive Processing", f"{avg_cogproc:.2f}%")

        with col2:
            if 'certainty' in df.columns:
                avg_cert = df['certainty'].mean()
                st.metric("Avg Certainty", f"{avg_cert:.2f}%")

        with col3:
            if 'tentative' in df.columns:
                avg_tent = df['tentative'].mean()
                st.metric("Avg Tentative Language", f"{avg_tent:.2f}%")

        # Distribution plots
        st.markdown("### Cognitive Processes Distribution")

        fig = go.Figure()

        for col in cognitive_cols:
            fig.add_trace(go.Box(
                y=df[col],
                name=col.capitalize(),
                boxmean='sd'
            ))

        fig.update_layout(
            title="Distribution of Cognitive Process Scores",
            yaxis_title="LIWC Score (%)",
            showlegend=True,
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

        # Correlation
        if len(cognitive_cols) > 1:
            st.markdown("### Cognitive Process Correlations")
            corr = df[cognitive_cols].corr()

            fig = px.imshow(
                corr,
                labels=dict(color="Correlation"),
                x=cognitive_cols,
                y=cognitive_cols,
                color_continuous_scale='RdBu_r',
                zmin=-1, zmax=1
            )

            fig.update_layout(title="Correlation Matrix", height=400)
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("### Emotional Processes Analysis")

    st.markdown("""
    **LIWC Emotional Categories:**
    - **Affect**: General emotional expression
    - **Posemo**: Positive emotions (happy, joy, love)
    - **Negemo**: Negative emotions (sad, angry, hate)
    - **Anx**: Anxiety (worry, fear, nervous)
    """)

    emotional_cols = ['affect', 'posemo', 'negemo']
    emotional_cols = [c for c in emotional_cols if c in df.columns]

    if emotional_cols:
        # Overall metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            if 'affect' in df.columns:
                avg_affect = df['affect'].mean()
                st.metric("Avg Emotional Expression", f"{avg_affect:.2f}%")

        with col2:
            if 'posemo' in df.columns:
                avg_pos = df['posemo'].mean()
                st.metric("Avg Positive Emotion", f"{avg_pos:.2f}%")

        with col3:
            if 'negemo' in df.columns:
                avg_neg = df['negemo'].mean()
                st.metric("Avg Negative Emotion", f"{avg_neg:.2f}%")

        # Emotion ratio
        if 'posemo' in df.columns and 'negemo' in df.columns:
            df['emotion_ratio'] = df['posemo'] / (df['negemo'] + 0.1)  # Avoid division by zero

            st.markdown("### Positive vs. Negative Emotion Balance")

            fig = px.scatter(
                df.sample(min(500, len(df))),
                x='posemo',
                y='negemo',
                title="Positive vs. Negative Emotions",
                labels={'posemo': 'Positive Emotion (%)', 'negemo': 'Negative Emotion (%)'},
                trendline="ols"
            )

            fig.add_shape(
                type="line",
                x0=0, y0=0,
                x1=df[['posemo', 'negemo']].max().max(),
                y1=df[['posemo', 'negemo']].max().max(),
                line=dict(color="red", dash="dash")
            )

            st.plotly_chart(fig, use_container_width=True)

        # Emotion distribution over score
        if 'score' in df.columns and 'affect' in df.columns:
            st.markdown("### Emotional Expression vs. Post Engagement")

            fig = px.scatter(
                df.sample(min(1000, len(df))),
                x='affect',
                y='score',
                title="Emotional Expression vs. Post Score",
                labels={'affect': 'Emotional Expression (%)', 'score': 'Post Score'},
                trendline="lowess"
            )

            st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("### PADM (Protective Action Decision Model) Analysis")

    st.markdown("""
    **PADM Components:**
    - **Risk Perception**: Awareness of danger (risk, danger, threat words)
    - **Social Influence**: Community coordination (social, family, friend words)
    - **Behavioral Response**: Action orientation (motion, space words)
    """)

    padm_cols = ['risk', 'social']
    padm_cols = [c for c in padm_cols if c in df.columns]

    if padm_cols:
        # PADM metrics
        col1, col2 = st.columns(2)

        with col1:
            if 'risk' in df.columns:
                avg_risk = df['risk'].mean()
                st.metric("Avg Risk Perception", f"{avg_risk:.2f}%")

                # Risk level classification
                high_risk = len(df[df['risk'] > df['risk'].quantile(0.75)])
                st.markdown(f"**High Risk Posts**: {high_risk} ({high_risk/len(df)*100:.1f}%)")

        with col2:
            if 'social' in df.columns:
                avg_social = df['social'].mean()
                st.metric("Avg Social Orientation", f"{avg_social:.2f}%")

                # Social posts
                high_social = len(df[df['social'] > df['social'].quantile(0.75)])
                st.markdown(f"**High Social Posts**: {high_social} ({high_social/len(df)*100:.1f}%)")

        # PADM Framework Visualization
        if len(padm_cols) >= 2:
            st.markdown("### PADM Component Analysis")

            fig = px.scatter(
                df.sample(min(1000, len(df))),
                x='risk',
                y='social',
                title="Risk Perception vs. Social Orientation",
                labels={'risk': 'Risk Perception (%)', 'social': 'Social Orientation (%)'},
                color='score' if 'score' in df.columns else None,
                size='num_comments' if 'num_comments' in df.columns else None
            )

            st.plotly_chart(fig, use_container_width=True)

    # Crisis phase analysis (if crisis_id available)
    if 'crisis_id' in df.columns:
        st.markdown("### PADM Analysis by Crisis")

        crisis_padm = df.groupby('crisis_id')[padm_cols].mean().reset_index()

        fig = go.Figure()

        for col in padm_cols:
            fig.add_trace(go.Bar(
                x=crisis_padm['crisis_id'],
                y=crisis_padm[col],
                name=col.capitalize()
            ))

        fig.update_layout(
            title="PADM Components by Crisis",
            xaxis_title="Crisis Event",
            yaxis_title="Average LIWC Score (%)",
            barmode='group',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.markdown("### Temporal Patterns in Cognitive & Emotional Processes")

    # Check for timestamp
    timestamp_col = None
    for col in ['created_utc', 'timestamp']:
        if col in df.columns:
            timestamp_col = col
            break

    if timestamp_col:
        df[timestamp_col] = pd.to_datetime(df[timestamp_col])
        df['date'] = df[timestamp_col].dt.date

        # Select LIWC category to visualize
        liwc_cols = [c for c in df.columns if c in ['cogproc', 'affect', 'posemo', 'negemo', 'risk', 'social', 'certainty']]

        if liwc_cols:
            selected_liwc = st.selectbox("Select LIWC Category", liwc_cols)

            # Aggregate by date
            daily_liwc = df.groupby('date').agg({
                selected_liwc: 'mean',
                'title': 'count'
            }).reset_index()

            daily_liwc.columns = ['date', 'avg_score', 'post_count']

            # Create dual-axis plot
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=daily_liwc['date'],
                y=daily_liwc['avg_score'],
                name=f'{selected_liwc.capitalize()} Score',
                line=dict(color='blue', width=2)
            ))

            fig.add_trace(go.Bar(
                x=daily_liwc['date'],
                y=daily_liwc['post_count'],
                name='Post Count',
                yaxis='y2',
                opacity=0.3,
                marker=dict(color='gray')
            ))

            fig.update_layout(
                title=f"{selected_liwc.capitalize()} Over Time",
                xaxis=dict(title="Date"),
                yaxis=dict(title=f"{selected_liwc.capitalize()} Score (%)"),
                yaxis2=dict(title="Number of Posts", overlaying='y', side='right'),
                hovermode='x unified',
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)

            # Show trend
            if len(daily_liwc) > 7:
                from scipy import stats
                x_numeric = list(range(len(daily_liwc)))
                slope, intercept, r_value, p_value, std_err = stats.linregress(x_numeric, daily_liwc['avg_score'])

                if slope > 0:
                    trend = "📈 Increasing"
                elif slope < 0:
                    trend = "📉 Decreasing"
                else:
                    trend = "➡️ Stable"

                st.info(f"""
                **Trend Analysis:**
                - Direction: {trend}
                - Correlation: {r_value:.3f}
                - Significance: {'✓ Significant' if p_value < 0.05 else '✗ Not significant'} (p={p_value:.4f})
                """)

    else:
        st.warning("⚠️ No timestamp column found for temporal analysis")

# Export LIWC scores
st.markdown("---")
st.markdown("### 📥 Export LIWC Data")

col1, col2 = st.columns(2)

with col1:
    if st.button("Download LIWC Scores (CSV)", use_container_width=True):
        liwc_cols = [c for c in df.columns if c in ['cogproc', 'affect', 'posemo', 'negemo', 'risk', 'social', 'certainty', 'tentative']]

        if liwc_cols:
            export_cols = ['title', 'author'] + liwc_cols
            export_cols = [c for c in export_cols if c in df.columns]

            csv = df[export_cols].to_csv(index=False)

            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            st.download_button(
                "Download CSV",
                data=csv,
                file_name=f"liwc_scores_{timestamp}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.error("No LIWC scores found in dataset")

with col2:
    st.info("""
    **Need to run LIWC analysis?**

    Use the LIWC integration script:
    ```bash
    python scripts/run_liwc_integration.py
    ```
    """)

# Footer
st.markdown("---")
st.markdown("""
💡 **LIWC Analysis Tips:**
- Higher scores indicate more frequent use of words in that category
- Compare scores across crises to identify behavioral patterns
- Use temporal analysis to track emotional evolution during crisis
- PADM framework helps understand protective action decision-making
""")
