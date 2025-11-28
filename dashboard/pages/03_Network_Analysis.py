import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

st.set_page_config(page_title="Network Analysis", page_icon="🔬", layout="wide")

st.title("🔬 Network Analysis")

st.markdown("""
Analyze user interaction networks and identify influential users during crisis events.
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
    return pd.read_csv(file_path)

df = load_data(selected_file)

st.success(f"✅ Loaded {len(df):,} posts")

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Network Metrics", "🌐 Network Visualization", "👥 Hub Analysis"])

with tab1:
    st.markdown("### Network Metrics")

    if 'author' not in df.columns:
        st.error("❌ Dataset missing 'author' column")
        st.stop()

    # Build simple network
    with st.spinner("Building network..."):
        G = nx.Graph()

        # Add nodes (users)
        authors = df['author'].unique()
        G.add_nodes_from(authors)

        # Add edges (users in same subreddit)
        if 'subreddit' in df.columns:
            for subreddit in df['subreddit'].unique():
                sub_authors = df[df['subreddit'] == subreddit]['author'].unique()
                # Create edges between users in same subreddit
                for i, author1 in enumerate(sub_authors):
                    for author2 in sub_authors[i+1:]:
                        if G.has_edge(author1, author2):
                            G[author1][author2]['weight'] += 1
                        else:
                            G.add_edge(author1, author2, weight=1)

    # Calculate metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Nodes (Users)", G.number_of_nodes())

    with col2:
        st.metric("Edges (Connections)", G.number_of_edges())

    with col3:
        density = nx.density(G) if G.number_of_nodes() > 0 else 0
        st.metric("Density", f"{density:.4f}")

    with col4:
        if G.number_of_edges() > 0:
            avg_degree = sum(dict(G.degree()).values()) / G.number_of_nodes()
            st.metric("Avg Degree", f"{avg_degree:.2f}")

    # More detailed metrics
    st.markdown("### Detailed Metrics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Connectivity")
        is_connected = nx.is_connected(G)
        num_components = nx.number_connected_components(G)

        st.markdown(f"- **Connected**: {'Yes' if is_connected else 'No'}")
        st.markdown(f"- **Components**: {num_components}")

        if not is_connected:
            largest_cc = max(nx.connected_components(G), key=len)
            st.markdown(f"- **Largest Component**: {len(largest_cc)} nodes")

    with col2:
        st.markdown("#### Degree Distribution")
        degrees = [d for n, d in G.degree()]
        if degrees:
            st.markdown(f"- **Min Degree**: {min(degrees)}")
            st.markdown(f"- **Max Degree**: {max(degrees)}")
            st.markdown(f"- **Median Degree**: {sorted(degrees)[len(degrees)//2]}")

with tab2:
    st.markdown("### Interactive Network Visualization")

    # Network size warning
    if G.number_of_nodes() > 200:
        st.warning(f"⚠️ Large network ({G.number_of_nodes()} nodes). Showing top 100 most connected users.")

        # Get top nodes by degree
        degrees = dict(G.degree())
        top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:100]
        top_node_names = [n[0] for n in top_nodes]

        G_viz = G.subgraph(top_node_names).copy()
    else:
        G_viz = G

    # Layout
    layout_type = st.selectbox(
        "Layout Algorithm",
        ["Spring", "Circular", "Random"],
        help="Choose how to position nodes"
    )

    if layout_type == "Spring":
        pos = nx.spring_layout(G_viz, k=0.5, iterations=50)
    elif layout_type == "Circular":
        pos = nx.circular_layout(G_viz)
    else:
        pos = nx.random_layout(G_viz)

    # Create plotly figure
    edge_trace = []
    for edge in G_viz.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace.append(
            go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=0.5, color='#888'),
                hoverinfo='none',
                showlegend=False
            )
        )

    # Node trace
    node_x = []
    node_y = []
    node_text = []
    node_size = []

    for node in G_viz.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"{node}<br>Degree: {G_viz.degree(node)}")
        node_size.append(min(G_viz.degree(node) * 3 + 5, 30))

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text,
        marker=dict(
            size=node_size,
            color=[G_viz.degree(node) for node in G_viz.nodes()],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Degree"),
            line=dict(width=0.5, color='white')
        )
    )

    # Create figure
    fig = go.Figure(data=edge_trace + [node_trace],
                    layout=go.Layout(
                        title=f"Network Graph ({G_viz.number_of_nodes()} nodes)",
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        height=600
                    ))

    st.plotly_chart(fig, use_container_width=True)

    # Export network
    if st.button("💾 Export Network Data"):
        # Save as GraphML
        output_dir = project_root / 'results' / 'networks'
        output_dir.mkdir(parents=True, exist_ok=True)

        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"network_{timestamp}.graphml"

        nx.write_graphml(G, output_path)
        st.success(f"✅ Network saved to: `{output_path.relative_to(project_root)}`")

with tab3:
    st.markdown("### Hub Analysis - Influential Users")

    # Calculate centrality measures
    with st.spinner("Calculating centrality measures..."):
        degree_cent = nx.degree_centrality(G)
        betweenness_cent = nx.betweenness_centrality(G)

        # Try to calculate others for connected graph
        if nx.is_connected(G):
            closeness_cent = nx.closeness_centrality(G)
        else:
            # Use largest component
            largest_cc = max(nx.connected_components(G), key=len)
            G_connected = G.subgraph(largest_cc).copy()
            closeness_cent = nx.closeness_centrality(G_connected)

    # Create DataFrame
    hub_data = []
    for node in G.nodes():
        hub_data.append({
            'User': node,
            'Degree Centrality': degree_cent.get(node, 0),
            'Betweenness Centrality': betweenness_cent.get(node, 0),
            'Closeness Centrality': closeness_cent.get(node, 0),
            'Posts': len(df[df['author'] == node]),
            'Total Score': df[df['author'] == node]['score'].sum() if 'score' in df.columns else 0
        })

    hub_df = pd.DataFrame(hub_data)

    # Sort options
    col1, col2 = st.columns([3, 1])

    with col1:
        sort_by = st.selectbox(
            "Sort by",
            ["Degree Centrality", "Betweenness Centrality", "Closeness Centrality", "Posts", "Total Score"]
        )

    with col2:
        top_n = st.number_input("Show top N", min_value=5, max_value=50, value=10)

    hub_df_sorted = hub_df.sort_values(sort_by, ascending=False).head(top_n)

    st.markdown(f"### Top {top_n} Users by {sort_by}")
    st.dataframe(hub_df_sorted, use_container_width=True)

    # Visualize top hubs
    import plotly.express as px

    fig = px.bar(
        hub_df_sorted,
        x='User',
        y=sort_by,
        title=f"Top {top_n} Users by {sort_by}",
        labels={sort_by: sort_by, 'User': 'User'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    # Hub types classification
    st.markdown("### Hub Classification")

    st.markdown("""
    **Hub Types:**
    - **Structural Hubs**: High degree centrality (many connections)
    - **Information Brokers**: High betweenness centrality (bridge communities)
    - **Core Users**: High closeness centrality (close to all users)
    """)

    # Classify hubs
    threshold_percentile = 90

    degree_threshold = hub_df['Degree Centrality'].quantile(threshold_percentile / 100)
    between_threshold = hub_df['Betweenness Centrality'].quantile(threshold_percentile / 100)
    close_threshold = hub_df['Closeness Centrality'].quantile(threshold_percentile / 100)

    hub_df['Structural Hub'] = hub_df['Degree Centrality'] >= degree_threshold
    hub_df['Information Broker'] = hub_df['Betweenness Centrality'] >= between_threshold
    hub_df['Core User'] = hub_df['Closeness Centrality'] >= close_threshold

    col1, col2, col3 = st.columns(3)

    with col1:
        structural_hubs = hub_df[hub_df['Structural Hub']]
        st.metric("Structural Hubs", len(structural_hubs))
        if len(structural_hubs) > 0:
            st.markdown("**Top 3:**")
            for user in structural_hubs.nlargest(3, 'Degree Centrality')['User']:
                st.markdown(f"- {user}")

    with col2:
        info_brokers = hub_df[hub_df['Information Broker']]
        st.metric("Information Brokers", len(info_brokers))
        if len(info_brokers) > 0:
            st.markdown("**Top 3:**")
            for user in info_brokers.nlargest(3, 'Betweenness Centrality')['User']:
                st.markdown(f"- {user}")

    with col3:
        core_users = hub_df[hub_df['Core User']]
        st.metric("Core Users", len(core_users))
        if len(core_users) > 0:
            st.markdown("**Top 3:**")
            for user in core_users.nlargest(3, 'Closeness Centrality')['User']:
                st.markdown(f"- {user}")

# Footer
st.markdown("---")
st.markdown("""
💡 **Network Analysis Tips:**
- Larger nodes = more connections
- Use the layout selector to find the best visualization
- Export network data for use in external tools like Gephi
""")
