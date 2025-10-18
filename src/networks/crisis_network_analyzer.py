"""
Crisis Network Analysis Framework - Week 3 Implementation
Multi-layer network construction and basic metrics for crisis communication analysis

Features:
- Multi-layer network construction (user, content, temporal, geographic)
- Basic network metrics calculation
- Crisis-specific hub identification
- Cross-crisis comparative analysis  
- Network visualization capabilities
- Integration with project structure
"""

import pandas as pd
import networkx as nx
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from collections import defaultdict, Counter
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import SpectralClustering
import community as community_louvain
import warnings
warnings.filterwarnings('ignore')

# Try to import project utilities
try:
    from src.utils.config_loader import get_config
    from src.utils.logger import get_logger
    HAS_PROJECT_UTILS = True
except ImportError:
    HAS_PROJECT_UTILS = False

class CrisisNetworkAnalyzer:
    """Comprehensive crisis network analysis framework"""
    
    def __init__(self, master_data_file: str):
        """Initialize the crisis network analyzer"""
        
        # Load master dataset
        self.df = pd.read_csv(master_data_file)
        print(f"Loaded master dataset: {len(self.df)} posts")
        
        # Initialize utilities if available
        if HAS_PROJECT_UTILS:
            try:
                self.config = get_config()
                self.logger = get_logger('crisis_network_analyzer')
            except:
                self.config = None
                self.logger = None
        else:
            self.config = None
            self.logger = None
        
        # Prepare data
        self._prepare_data()
        
        # Network storage
        self.networks = {}
        self.metrics = {}
        
        # Output directories
        self.output_dir = Path('results/networks')
        self.viz_dir = Path('results/visualizations')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.viz_dir.mkdir(parents=True, exist_ok=True)
        
        print("Crisis Network Analyzer initialized")
    
    def _prepare_data(self):
        """Prepare and clean data for network analysis"""
        
        # Ensure required columns exist
        required_cols = ['title', 'content', 'author', 'subreddit', 'created_utc', 'score']
        missing_cols = [col for col in required_cols if col not in self.df.columns]
        
        if missing_cols:
            print(f"Warning: Missing columns {missing_cols} - some analyses may be limited")
        
        # Convert dates
        if 'created_utc' in self.df.columns:
            self.df['created_utc'] = pd.to_datetime(self.df['created_utc'])
            self.df['date'] = self.df['created_utc'].dt.date
            self.df['hour'] = self.df['created_utc'].dt.hour
        
        # Clean text data
        if 'content' in self.df.columns:
            self.df['content_clean'] = self.df['content'].fillna('').str.lower()
            self.df['content_length'] = self.df['content'].str.len()
        
        # Extract crisis information
        if 'crisis_id' in self.df.columns:
            self.crisis_types = self.df['crisis_id'].unique()
            print(f"Found {len(self.crisis_types)} crisis types: {list(self.crisis_types)}")
        else:
            self.crisis_types = ['unknown']
        
        # Create engagement categories
        if 'score' in self.df.columns:
            self.df['engagement_category'] = pd.cut(
                self.df['score'], 
                bins=[-np.inf, 10, 100, 1000, np.inf],
                labels=['low', 'medium', 'high', 'viral']
            )
        
        print(f"Data preparation complete: {len(self.df)} posts ready for analysis")
    
    def build_user_interaction_network(self, crisis_id: Optional[str] = None) -> nx.Graph:
        """Build user interaction network based on shared subreddits and topics"""
        
        # Filter data if specific crisis requested
        if crisis_id and 'crisis_id' in self.df.columns:
            data = self.df[self.df['crisis_id'] == crisis_id].copy()
            network_name = f"user_interaction_{crisis_id}"
        else:
            data = self.df.copy()
            network_name = "user_interaction_all"
        
        print(f"Building user interaction network: {len(data)} posts")
        
        # Create user-subreddit bipartite graph
        G = nx.Graph()
        
        # Add nodes and edges based on user-subreddit interactions
        for _, row in data.iterrows():
            user = row.get('author', 'unknown')
            subreddit = row.get('subreddit', 'unknown')
            
            if user != '[deleted]' and user != 'unknown':
                # Add edge with weight based on engagement
                weight = max(1, row.get('score', 1))
                
                if G.has_edge(user, subreddit):
                    G[user][subreddit]['weight'] += weight
                    G[user][subreddit]['post_count'] += 1
                else:
                    G.add_edge(user, subreddit, weight=weight, post_count=1)
        
        # Convert to user-user network by finding users in same subreddits
        user_network = nx.Graph()
        
        # Get all users
        users = [n for n in G.nodes() if n in data['author'].values]
        
        # Connect users who post in same subreddits
        for i, user1 in enumerate(users):
            for user2 in users[i+1:]:
                # Find common subreddits
                user1_subreddits = set(G.neighbors(user1))
                user2_subreddits = set(G.neighbors(user2))
                common_subreddits = user1_subreddits.intersection(user2_subreddits)
                
                if common_subreddits:
                    # Weight by number of common subreddits and engagement
                    weight = len(common_subreddits)
                    user_network.add_edge(user1, user2, weight=weight, 
                                        common_subreddits=list(common_subreddits))
        
        self.networks[network_name] = user_network
        print(f"User network created: {user_network.number_of_nodes()} users, {user_network.number_of_edges()} connections")
        
        return user_network
    
    def build_content_similarity_network(self, crisis_id: Optional[str] = None, 
                                       similarity_threshold: float = 0.3) -> nx.Graph:
        """Build content similarity network using TF-IDF and cosine similarity"""
        
        # Filter data
        if crisis_id and 'crisis_id' in self.df.columns:
            data = self.df[self.df['crisis_id'] == crisis_id].copy()
            network_name = f"content_similarity_{crisis_id}"
        else:
            data = self.df.copy()
            network_name = "content_similarity_all"
        
        print(f"Building content similarity network: {len(data)} posts")
        
        # Prepare text data
        texts = data['content_clean'].fillna('').tolist()
        post_ids = data['post_id'].tolist() if 'post_id' in data.columns else range(len(data))
        
        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(texts)
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # Build network
            G = nx.Graph()
            
            # Add nodes with metadata
            for i, (_, row) in enumerate(data.iterrows()):
                G.add_node(post_ids[i], 
                          title=row.get('title', ''),
                          author=row.get('author', ''),
                          subreddit=row.get('subreddit', ''),
                          score=row.get('score', 0))
            
            # Add edges based on similarity threshold
            for i in range(len(similarity_matrix)):
                for j in range(i+1, len(similarity_matrix)):
                    similarity = similarity_matrix[i, j]
                    if similarity > similarity_threshold:
                        G.add_edge(post_ids[i], post_ids[j], 
                                  similarity=similarity,
                                  weight=similarity)
            
            self.networks[network_name] = G
            print(f"Content network created: {G.number_of_nodes()} posts, {G.number_of_edges()} similarity connections")
            
            return G
            
        except Exception as e:
            print(f"Error building content similarity network: {e}")
            return nx.Graph()
    
    def build_temporal_network(self, crisis_id: Optional[str] = None, 
                             time_window_hours: int = 24) -> nx.Graph:
        """Build temporal network showing information flow over time"""
        
        # Filter data
        if crisis_id and 'crisis_id' in self.df.columns:
            data = self.df[self.df['crisis_id'] == crisis_id].copy()
            network_name = f"temporal_{crisis_id}"
        else:
            data = self.df.copy()
            network_name = "temporal_all"
        
        if 'created_utc' not in data.columns:
            print("Warning: No temporal data available")
            return nx.Graph()
        
        print(f"Building temporal network: {len(data)} posts")
        
        # Sort by time
        data = data.sort_values('created_utc')
        
        G = nx.DiGraph()  # Directed graph for temporal flow
        
        # Add nodes
        for _, row in data.iterrows():
            node_id = row.get('post_id', f"post_{row.name}")
            G.add_node(node_id,
                      timestamp=row['created_utc'],
                      author=row.get('author', ''),
                      subreddit=row.get('subreddit', ''),
                      score=row.get('score', 0),
                      title=row.get('title', '')[:50])
        
        # Add temporal edges (posts within time window)
        posts = list(data.itertuples())
        
        for i, post1 in enumerate(posts):
            post1_time = post1.created_utc
            post1_id = getattr(post1, 'post_id', f"post_{post1.Index}")
            
            # Look forward in time window
            for post2 in posts[i+1:]:
                post2_time = post2.created_utc
                time_diff = (post2_time - post1_time).total_seconds() / 3600  # hours
                
                if time_diff > time_window_hours:
                    break  # Posts are sorted, so we can break here
                
                post2_id = getattr(post2, 'post_id', f"post_{post2.Index}")
                
                # Add edge if posts are related (same subreddit or author)
                if (post1.subreddit == post2.subreddit or 
                    post1.author == post2.author):
                    
                    # Weight by temporal proximity and engagement
                    temporal_weight = 1 / (time_diff + 1)  # Closer in time = higher weight
                    engagement_weight = (post1.score + post2.score) / 2
                    
                    G.add_edge(post1_id, post2_id,
                              time_diff_hours=time_diff,
                              weight=temporal_weight * engagement_weight,
                              relationship='temporal_flow')
        
        self.networks[network_name] = G
        print(f"Temporal network created: {G.number_of_nodes()} posts, {G.number_of_edges()} temporal connections")
        
        return G
    
    def build_subreddit_network(self, crisis_id: Optional[str] = None) -> nx.Graph:
        """Build subreddit interaction network"""
        
        # Filter data
        if crisis_id and 'crisis_id' in self.df.columns:
            data = self.df[self.df['crisis_id'] == crisis_id].copy()
            network_name = f"subreddit_{crisis_id}"
        else:
            data = self.df.copy()
            network_name = "subreddit_all"
        
        print(f"Building subreddit network: {len(data)} posts")
        
        G = nx.Graph()
        
        # Count posts per subreddit
        subreddit_stats = data.groupby('subreddit').agg({
            'score': ['sum', 'mean', 'count'],
            'author': 'nunique'
        }).round(2)
        
        # Add subreddit nodes
        for subreddit in data['subreddit'].unique():
            if subreddit and subreddit != 'unknown':
                stats = subreddit_stats.loc[subreddit]
                G.add_node(subreddit,
                          post_count=stats[('score', 'count')],
                          total_score=stats[('score', 'sum')],
                          avg_score=stats[('score', 'mean')],
                          unique_authors=stats[('author', 'nunique')])
        
        # Connect subreddits based on shared authors
        subreddits = list(G.nodes())
        
        for i, sub1 in enumerate(subreddits):
            for sub2 in subreddits[i+1:]:
                # Find users who post in both subreddits
                sub1_authors = set(data[data['subreddit'] == sub1]['author'])
                sub2_authors = set(data[data['subreddit'] == sub2]['author'])
                shared_authors = sub1_authors.intersection(sub2_authors)
                
                if shared_authors:
                    # Weight by number of shared authors
                    weight = len(shared_authors)
                    G.add_edge(sub1, sub2, weight=weight, 
                              shared_authors=len(shared_authors))
        
        self.networks[network_name] = G
        print(f"Subreddit network created: {G.number_of_nodes()} subreddits, {G.number_of_edges()} connections")
        
        return G
    
    def calculate_basic_metrics(self, network_name: str) -> Dict[str, Any]:
        """Calculate basic network metrics"""
        
        if network_name not in self.networks:
            print(f"Network {network_name} not found")
            return {}
        
        G = self.networks[network_name]
        
        print(f"Calculating metrics for {network_name}")
        
        metrics = {
            'basic_stats': {
                'nodes': G.number_of_nodes(),
                'edges': G.number_of_edges(),
                'density': nx.density(G),
                'is_connected': nx.is_connected(G) if not G.is_directed() else nx.is_weakly_connected(G)
            }
        }
        
        if metrics['basic_stats']['nodes'] > 0:
            # Degree statistics
            if G.is_directed():
                in_degrees = [d for n, d in G.in_degree()]
                out_degrees = [d for n, d in G.out_degree()]
                metrics['degree_stats'] = {
                    'avg_in_degree': np.mean(in_degrees),
                    'avg_out_degree': np.mean(out_degrees),
                    'max_in_degree': max(in_degrees) if in_degrees else 0,
                    'max_out_degree': max(out_degrees) if out_degrees else 0
                }
            else:
                degrees = [d for n, d in G.degree()]
                metrics['degree_stats'] = {
                    'avg_degree': np.mean(degrees),
                    'max_degree': max(degrees) if degrees else 0,
                    'degree_std': np.std(degrees)
                }
            
            # Clustering
            if not G.is_directed():
                try:
                    metrics['clustering'] = {
                        'avg_clustering': nx.average_clustering(G),
                        'transitivity': nx.transitivity(G)
                    }
                except:
                    metrics['clustering'] = {'avg_clustering': 0, 'transitivity': 0}
            
            # Path lengths (on largest connected component)
            try:
                if G.is_directed():
                    if nx.is_weakly_connected(G):
                        largest_cc = G
                    else:
                        largest_cc = max(nx.weakly_connected_components(G), key=len)
                        largest_cc = G.subgraph(largest_cc)
                else:
                    if nx.is_connected(G):
                        largest_cc = G
                    else:
                        largest_cc = max(nx.connected_components(G), key=len)
                        largest_cc = G.subgraph(largest_cc)
                
                if largest_cc.number_of_nodes() > 1:
                    metrics['path_lengths'] = {
                        'avg_shortest_path': nx.average_shortest_path_length(largest_cc),
                        'diameter': nx.diameter(largest_cc)
                    }
            except:
                metrics['path_lengths'] = {'avg_shortest_path': 0, 'diameter': 0}
            
            # Community detection (for undirected graphs)
            if not G.is_directed() and G.number_of_edges() > 0:
                try:
                    communities = community_louvain.best_partition(G)
                    metrics['communities'] = {
                        'num_communities': len(set(communities.values())),
                        'modularity': community_louvain.modularity(communities, G)
                    }
                except:
                    metrics['communities'] = {'num_communities': 0, 'modularity': 0}
        
        self.metrics[network_name] = metrics
        
        return metrics
    
    def identify_crisis_hubs(self, network_name: str, top_k: int = 10) -> Dict[str, List]:
        """Identify different types of crisis communication hubs"""
        
        if network_name not in self.networks:
            return {}
        
        G = self.networks[network_name]
        hubs = {}
        
        print(f"Identifying hubs in {network_name}")
        
        # 1. Structural Hubs (high degree)
        if G.is_directed():
            in_degree_centrality = nx.in_degree_centrality(G)
            out_degree_centrality = nx.out_degree_centrality(G)
            hubs['high_in_degree'] = sorted(in_degree_centrality.items(), 
                                          key=lambda x: x[1], reverse=True)[:top_k]
            hubs['high_out_degree'] = sorted(out_degree_centrality.items(), 
                                           key=lambda x: x[1], reverse=True)[:top_k]
        else:
            degree_centrality = nx.degree_centrality(G)
            hubs['high_degree'] = sorted(degree_centrality.items(), 
                                       key=lambda x: x[1], reverse=True)[:top_k]
        
        # 2. Betweenness Centrality (information brokers)
        try:
            betweenness = nx.betweenness_centrality(G, k=min(100, G.number_of_nodes()))
            hubs['information_brokers'] = sorted(betweenness.items(), 
                                               key=lambda x: x[1], reverse=True)[:top_k]
        except:
            hubs['information_brokers'] = []
        
        # 3. Closeness Centrality (quick information spread)
        try:
            closeness = nx.closeness_centrality(G)
            hubs['quick_spreaders'] = sorted(closeness.items(), 
                                           key=lambda x: x[1], reverse=True)[:top_k]
        except:
            hubs['quick_spreaders'] = []
        
        # 4. Eigenvector Centrality (connected to important nodes)
        try:
            eigenvector = nx.eigenvector_centrality(G, max_iter=1000)
            hubs['influence_leaders'] = sorted(eigenvector.items(), 
                                             key=lambda x: x[1], reverse=True)[:top_k]
        except:
            hubs['influence_leaders'] = []
        
        return hubs
    
    def analyze_all_networks(self, crisis_id: Optional[str] = None):
        """Perform comprehensive network analysis"""
        
        print(f"Starting comprehensive network analysis for crisis: {crisis_id or 'all'}")
        
        # Build all network types
        networks_built = {}
        
        # User interaction network
        try:
            user_net = self.build_user_interaction_network(crisis_id)
            networks_built['user_interaction'] = len(user_net.nodes())
        except Exception as e:
            print(f"Error building user network: {e}")
        
        # Content similarity network
        try:
            content_net = self.build_content_similarity_network(crisis_id)
            networks_built['content_similarity'] = len(content_net.nodes())
        except Exception as e:
            print(f"Error building content network: {e}")
        
        # Temporal network
        try:
            temporal_net = self.build_temporal_network(crisis_id)
            networks_built['temporal'] = len(temporal_net.nodes())
        except Exception as e:
            print(f"Error building temporal network: {e}")
        
        # Subreddit network
        try:
            subreddit_net = self.build_subreddit_network(crisis_id)
            networks_built['subreddit'] = len(subreddit_net.nodes())
        except Exception as e:
            print(f"Error building subreddit network: {e}")
        
        # Calculate metrics for all networks
        all_metrics = {}
        all_hubs = {}
        
        for network_name in self.networks.keys():
            if crisis_id is None or crisis_id in network_name or 'all' in network_name:
                try:
                    metrics = self.calculate_basic_metrics(network_name)
                    all_metrics[network_name] = metrics
                    
                    hubs = self.identify_crisis_hubs(network_name)
                    all_hubs[network_name] = hubs
                except Exception as e:
                    print(f"Error analyzing {network_name}: {e}")
        
        # Save results
        self._save_analysis_results(crisis_id, all_metrics, all_hubs, networks_built)
        
        return {
            'networks_built': networks_built,
            'metrics': all_metrics,
            'hubs': all_hubs
        }
    
    def _save_analysis_results(self, crisis_id: Optional[str], metrics: Dict, 
                             hubs: Dict, networks_summary: Dict):
        """Save analysis results to files"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        crisis_label = crisis_id or 'all_crises'
        
        # Save metrics
        metrics_file = self.output_dir / f"{crisis_label}_network_metrics_{timestamp}.json"
        with open(metrics_file, 'w') as f:
            # Convert numpy types to Python types for JSON serialization
            def convert_types(obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                return obj
            
            def recursive_convert(d):
                if isinstance(d, dict):
                    return {k: recursive_convert(v) for k, v in d.items()}
                elif isinstance(d, list):
                    return [recursive_convert(i) for i in d]
                else:
                    return convert_types(d)
            
            json.dump(recursive_convert(metrics), f, indent=2)
        
        # Save hubs
        hubs_file = self.output_dir / f"{crisis_label}_network_hubs_{timestamp}.json"
        with open(hubs_file, 'w') as f:
            json.dump(hubs, f, indent=2)
        
        # Save summary report
        summary_file = self.output_dir / f"{crisis_label}_analysis_summary_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write(f"Crisis Network Analysis Report\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write(f"Crisis: {crisis_label}\n")
            f.write(f"Dataset: {len(self.df)} total posts\n\n")
            
            f.write("Networks Built:\n")
            for net_type, node_count in networks_summary.items():
                f.write(f"  {net_type}: {node_count} nodes\n")
            
            f.write(f"\nDetailed metrics saved to: {metrics_file.name}\n")
            f.write(f"Hub analysis saved to: {hubs_file.name}\n")
        
        print(f"Analysis results saved to {self.output_dir}")

def run_crisis_network_analysis(master_data_file: str):
    """Run complete crisis network analysis"""
    
    print("CRISIS NETWORK ANALYSIS - Week 3 Implementation")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = CrisisNetworkAnalyzer(master_data_file)
    
    # Analyze each crisis separately
    if hasattr(analyzer, 'crisis_types'):
        for crisis_id in analyzer.crisis_types:
            if crisis_id != 'unknown':
                print(f"\nAnalyzing {crisis_id}...")
                try:
                    results = analyzer.analyze_all_networks(crisis_id)
                    print(f"✅ {crisis_id} analysis complete")
                except Exception as e:
                    print(f"❌ Error analyzing {crisis_id}: {e}")
    
    # Overall analysis across all crises
    print(f"\nAnalyzing all crises combined...")
    try:
        overall_results = analyzer.analyze_all_networks(None)
        print(f"✅ Overall analysis complete")
    except Exception as e:
        print(f"❌ Error in overall analysis: {e}")
    
    # Print summary
    print(f"\n📊 NETWORK ANALYSIS SUMMARY")
    print(f"Networks available: {list(analyzer.networks.keys())}")
    print(f"Results saved to: results/networks/")
    
    return analyzer

if __name__ == "__main__":
    # Use the most recent master dataset file
    import glob
    master_files = glob.glob('data/raw/MASTER_reddit_crisis_data_*.csv')
    
    if master_files:
        latest_file = max(master_files, key=lambda f: f.split('_')[-1])
        print(f"Using master dataset: {latest_file}")
        analyzer = run_crisis_network_analysis(latest_file)
    else:
        print("No master dataset found. Please run the data combination script first.")
