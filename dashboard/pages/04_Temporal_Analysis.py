import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

st.set_page_config(page_title="Temporal Analysis", page_icon="📊", layout="wide")

st.title("Temporal Analysis")

st.markdown("""
Analyze how crisis activity and behavior patterns evolve over time.
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
    st.warning("No datasets found!")
    st.markdown("""
    **Get started:**
    1. Go to the **Data Collection** page to collect new data
    2. Or upload an existing CSV file
    """)
    st.stop()

# Dataset selector
file_options = {f"{f.name} ({source})": (f, source) for f, source in csv_files}
selected_file_name = st.selectbox("Select Dataset", options=list(file_options.keys()))
selected_file, source = file_options[selected_file_name]

# Load data
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    
    # Convert timestamps
    timestamp_cols = ['created_utc', 'timestamp', 'collection_timestamp']
    for col in timestamp_cols:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                break
            except:
                pass
    
    return df

try:
    df = load_data(selected_file)
    st.success(f"Loaded {len(df):,} posts")
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Identify timestamp column
timestamp_col = None
for col in ['created_utc', 'timestamp', 'collection_timestamp']:
    if col in df.columns and pd.api.types.is_datetime64_any_dtype(df[col]):
        timestamp_col = col
        break

if timestamp_col is None:
    st.error("No timestamp column found in the dataset!")
    st.info("Dataset should have 'created_utc', 'timestamp', or 'collection_timestamp' column.")
    st.stop()

# Filter out invalid timestamps
df = df[df[timestamp_col].notna()].copy()

if len(df) == 0:
    st.error("No valid timestamps found in the dataset!")
    st.stop()

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Time Series", 
    "Peak Activity", 
    "Crisis Phases",
    "Hourly Patterns"
])

with tab1:
    st.markdown("### Activity Over Time")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        # Aggregation options
        time_unit = st.selectbox(
            "Time Granularity",
            ["Hour", "Day", "Week"],
            index=1
        )
        
        show_cumulative = st.checkbox("Show Cumulative", value=False)
    
    with col1:
        # Resample data based on time unit
        df['date'] = df[timestamp_col]
        
        if time_unit == "Hour":
            df['time_bucket'] = df['date'].dt.floor('H')
        elif time_unit == "Day":
            df['time_bucket'] = df['date'].dt.floor('D')
        else:  # Week
            df['time_bucket'] = df['date'].dt.to_period('W').dt.start_time
        
        time_series = df.groupby('time_bucket').size().reset_index(name='count')
        
        if show_cumulative:
            time_series['count'] = time_series['count'].cumsum()
        
        # Create time series plot
        fig = px.line(
            time_series,
            x='time_bucket',
            y='count',
            title=f"Post Activity by {time_unit}",
            labels={'time_bucket': 'Time', 'count': 'Cumulative Posts' if show_cumulative else 'Post Count'}
        )
        fig.update_traces(line_color='#1f77b4', line_width=2)
        fig.update_layout(height=400, hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
    
    # Show summary statistics
    st.markdown("#### Time Period Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        start_date = df['date'].min()
        st.metric("Start Date", start_date.strftime('%Y-%m-%d'))
    
    with col2:
        end_date = df['date'].max()
        st.metric("End Date", end_date.strftime('%Y-%m-%d'))
    
    with col3:
        duration = (end_date - start_date).days
        st.metric("Duration", f"{duration} days")
    
    with col4:
        avg_daily = len(df) / max(duration, 1)
        st.metric("Avg Posts/Day", f"{avg_daily:.0f}")

with tab2:
    st.markdown("### Peak Activity Analysis")
    
    # Find peak periods
    df['date_only'] = df[timestamp_col].dt.date
    daily_counts = df.groupby('date_only').size().reset_index(name='count')
    daily_counts = daily_counts.sort_values('count', ascending=False)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Bar chart of top 10 days
        top_days = daily_counts.head(10)
        fig = px.bar(
            top_days,
            x='date_only',
            y='count',
            title="Top 10 Most Active Days",
            labels={'date_only': 'Date', 'count': 'Post Count'},
            color='count',
            color_continuous_scale='Reds'
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Top 5 Peak Days")
        for idx, row in daily_counts.head(5).iterrows():
            st.metric(
                str(row['date_only']),
                f"{row['count']} posts"
            )
    
    # Identify crisis phases based on activity
    st.markdown("---")
    st.markdown("#### Activity Distribution")
    
    # Calculate quartiles
    q1 = daily_counts['count'].quantile(0.25)
    q2 = daily_counts['count'].quantile(0.50)
    q3 = daily_counts['count'].quantile(0.75)
    
    def categorize_activity(count):
        if count >= q3:
            return "High Activity"
        elif count >= q2:
            return "Moderate Activity"
        elif count >= q1:
            return "Low Activity"
        else:
            return "Minimal Activity"
    
    daily_counts['activity_level'] = daily_counts['count'].apply(categorize_activity)
    activity_summary = daily_counts['activity_level'].value_counts()
    
    fig = px.pie(
        values=activity_summary.values,
        names=activity_summary.index,
        title="Distribution of Activity Levels",
        color_discrete_sequence=px.colors.sequential.Reds_r
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("### Crisis Phase Analysis")
    
    st.markdown("""
    Crisis events typically follow distinct phases. This analysis identifies potential phases
    based on activity patterns and temporal dynamics.
    """)
    
    # Simple phase detection based on activity changes
    daily_counts_sorted = df.groupby('date_only').size().reset_index(name='count')
    daily_counts_sorted = daily_counts_sorted.sort_values('date_only')
    
    if len(daily_counts_sorted) >= 7:
        # Calculate rolling average
        daily_counts_sorted['rolling_avg'] = daily_counts_sorted['count'].rolling(window=3, center=True).mean()
        
        # Detect phases
        max_count = daily_counts_sorted['count'].max()
        threshold_high = max_count * 0.7
        threshold_low = max_count * 0.3
        
        def detect_phase(row):
            if row['count'] >= threshold_high:
                return "Peak Crisis"
            elif row['count'] >= threshold_low:
                return "Active Phase"
            else:
                return "Recovery/Monitoring"
        
        daily_counts_sorted['phase'] = daily_counts_sorted.apply(detect_phase, axis=1)
        
        # Visualize phases
        fig = go.Figure()
        
        # Add bars colored by phase
        colors = {
            "Peak Crisis": "#d62728",
            "Active Phase": "#ff7f0e",
            "Recovery/Monitoring": "#2ca02c"
        }
        
        for phase in daily_counts_sorted['phase'].unique():
            phase_data = daily_counts_sorted[daily_counts_sorted['phase'] == phase]
            fig.add_trace(go.Bar(
                x=phase_data['date_only'],
                y=phase_data['count'],
                name=phase,
                marker_color=colors.get(phase, '#1f77b4')
            ))
        
        # Add rolling average line
        fig.add_trace(go.Scatter(
            x=daily_counts_sorted['date_only'],
            y=daily_counts_sorted['rolling_avg'],
            name='3-Day Average',
            line=dict(color='black', width=2, dash='dash'),
            mode='lines'
        ))
        
        fig.update_layout(
            title="Crisis Phases Based on Activity Patterns",
            xaxis_title="Date",
            yaxis_title="Post Count",
            height=400,
            barmode='stack',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Phase summary
        st.markdown("#### Phase Distribution")
        phase_counts = daily_counts_sorted.groupby('phase').agg({
            'date_only': 'count',
            'count': 'sum'
        }).reset_index()
        phase_counts.columns = ['Phase', 'Days', 'Total Posts']
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.dataframe(phase_counts, use_container_width=True, hide_index=True)
        
        with col2:
            fig = px.pie(
                phase_counts,
                values='Days',
                names='Phase',
                title="Days per Phase",
                color='Phase',
                color_discrete_map=colors
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Need at least 7 days of data for phase analysis.")

with tab4:
    st.markdown("### Hourly Activity Patterns")
    
    # Extract hour and day of week
    df['hour'] = df[timestamp_col].dt.hour
    df['day_of_week'] = df[timestamp_col].dt.day_name()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Hourly distribution
        hourly_counts = df.groupby('hour').size().reset_index(name='count')
        
        fig = px.bar(
            hourly_counts,
            x='hour',
            y='count',
            title="Posts by Hour of Day (24-hour format)",
            labels={'hour': 'Hour', 'count': 'Post Count'},
            color='count',
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=350, showlegend=False)
        fig.update_xaxes(dtick=2)
        st.plotly_chart(fig, use_container_width=True)
        
        # Peak hours
        peak_hour = hourly_counts.loc[hourly_counts['count'].idxmax(), 'hour']
        st.info(f"**Peak Activity Hour**: {peak_hour}:00 - {peak_hour+1}:00")
    
    with col2:
        # Day of week distribution
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_counts = df.groupby('day_of_week').size().reset_index(name='count')
        day_counts['day_of_week'] = pd.Categorical(day_counts['day_of_week'], categories=day_order, ordered=True)
        day_counts = day_counts.sort_values('day_of_week')
        
        fig = px.bar(
            day_counts,
            x='day_of_week',
            y='count',
            title="Posts by Day of Week",
            labels={'day_of_week': 'Day', 'count': 'Post Count'},
            color='count',
            color_continuous_scale='Greens'
        )
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Peak day
        peak_day = day_counts.loc[day_counts['count'].idxmax(), 'day_of_week']
        st.info(f"**Most Active Day**: {peak_day}")
    
    # Heatmap of hour vs day
    st.markdown("#### Activity Heatmap (Hour × Day of Week)")
    
    pivot_table = df.groupby(['day_of_week', 'hour']).size().reset_index(name='count')
    pivot_table['day_of_week'] = pd.Categorical(pivot_table['day_of_week'], categories=day_order, ordered=True)
    pivot = pivot_table.pivot(index='day_of_week', columns='hour', values='count').fillna(0)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='YlOrRd',
        hoverongaps=False
    ))
    
    fig.update_layout(
        title="Post Activity Heatmap",
        xaxis_title="Hour of Day",
        yaxis_title="Day of Week",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("**Tip**: Use temporal patterns to identify crisis escalation points and optimal communication windows.")
