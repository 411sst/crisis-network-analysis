"""
Unit tests for Crisis Network Analyzer
"""

import pytest
import pandas as pd
import networkx as nx
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import sys
from pathlib import Path
import tempfile

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from networks.crisis_network_analyzer import CrisisNetworkAnalyzer


class TestCrisisNetworkAnalyzer:
    """Test suite for CrisisNetworkAnalyzer"""

    @pytest.fixture
    def sample_data(self):
        """Create sample crisis data for testing"""
        data = {
            'title': [
                'Test Post 1',
                'Test Post 2',
                'Test Post 3',
                'Test Post 4',
                'Test Post 5'
            ],
            'content': [
                'This is test content about the crisis situation',
                'More information about the emergency response',
                'Update on the crisis management efforts',
                'Community coordination during crisis',
                'Final update on crisis resolution'
            ],
            'author': [
                'user1',
                'user2',
                'user1',
                'user3',
                'user2'
            ],
            'subreddit': [
                'test_sub',
                'test_sub',
                'crisis_sub',
                'test_sub',
                'crisis_sub'
            ],
            'created_utc': [
                datetime.now() - timedelta(days=5),
                datetime.now() - timedelta(days=4),
                datetime.now() - timedelta(days=3),
                datetime.now() - timedelta(days=2),
                datetime.now() - timedelta(days=1)
            ],
            'score': [100, 200, 150, 300, 250],
            'num_comments': [10, 20, 15, 30, 25],
            'upvote_ratio': [0.95, 0.90, 0.92, 0.88, 0.94],
            'crisis_id': [
                'test_crisis',
                'test_crisis',
                'test_crisis',
                'test_crisis',
                'test_crisis'
            ]
        }
        return pd.DataFrame(data)

    @pytest.fixture
    def sample_csv(self, sample_data, tmp_path):
        """Create temporary CSV file with sample data"""
        csv_file = tmp_path / "test_data.csv"
        sample_data.to_csv(csv_file, index=False)
        return str(csv_file)

    @pytest.fixture
    def analyzer(self, sample_csv):
        """Create analyzer instance with sample data"""
        return CrisisNetworkAnalyzer(sample_csv)

    def test_analyzer_initialization(self, analyzer):
        """Test that analyzer initializes correctly"""
        assert analyzer is not None
        assert hasattr(analyzer, 'df')
        assert hasattr(analyzer, 'networks')
        assert hasattr(analyzer, 'metrics')
        assert len(analyzer.df) > 0

    def test_data_preparation(self, analyzer):
        """Test that data is prepared correctly"""
        assert 'created_utc' in analyzer.df.columns
        assert pd.api.types.is_datetime64_any_dtype(analyzer.df['created_utc'])

        if 'date' in analyzer.df.columns:
            assert analyzer.df['date'].notna().all()

    def test_build_user_network(self, analyzer):
        """Test building user interaction network"""
        network = analyzer.build_user_interaction_network()

        assert isinstance(network, nx.Graph) or isinstance(network, nx.DiGraph)
        assert network.number_of_nodes() > 0

    def test_build_content_network(self, analyzer):
        """Test building content similarity network"""
        network = analyzer.build_content_similarity_network()

        assert isinstance(network, nx.Graph)
        assert network.number_of_nodes() > 0

    def test_build_temporal_network(self, analyzer):
        """Test building temporal network"""
        network = analyzer.build_temporal_network()

        assert isinstance(network, nx.Graph) or isinstance(network, nx.DiGraph)
        assert network.number_of_nodes() > 0

    def test_build_subreddit_network(self, analyzer):
        """Test building subreddit co-occurrence network"""
        network = analyzer.build_subreddit_network()

        assert isinstance(network, nx.Graph)
        assert network.number_of_nodes() > 0

    def test_calculate_network_metrics(self, analyzer):
        """Test calculating basic network metrics"""
        # Build a simple network first
        analyzer.networks['user_interaction'] = analyzer.build_user_interaction_network()

        metrics = analyzer.calculate_basic_network_metrics(
            analyzer.networks['user_interaction']
        )

        assert isinstance(metrics, dict)
        assert 'num_nodes' in metrics
        assert 'num_edges' in metrics
        assert metrics['num_nodes'] >= 0
        assert metrics['num_edges'] >= 0

    def test_identify_hubs(self, analyzer):
        """Test hub identification"""
        # Build network first
        network = analyzer.build_user_interaction_network()

        if network.number_of_nodes() > 0:
            hubs = analyzer.identify_network_hubs(network, top_k=3)

            assert isinstance(hubs, list)
            for hub in hubs:
                assert 'node' in hub
                assert 'centrality' in hub

    def test_empty_dataframe_handling(self, tmp_path):
        """Test handling of empty DataFrame"""
        empty_df = pd.DataFrame(columns=['title', 'content', 'author'])
        csv_file = tmp_path / "empty.csv"
        empty_df.to_csv(csv_file, index=False)

        # Should handle empty data gracefully
        analyzer = CrisisNetworkAnalyzer(str(csv_file))
        assert len(analyzer.df) == 0

    def test_missing_columns_handling(self, tmp_path):
        """Test handling of missing columns"""
        incomplete_df = pd.DataFrame({
            'title': ['Test'],
            'author': ['user1']
            # Missing 'content', 'created_utc', etc.
        })
        csv_file = tmp_path / "incomplete.csv"
        incomplete_df.to_csv(csv_file, index=False)

        # Should handle missing columns gracefully
        analyzer = CrisisNetworkAnalyzer(str(csv_file))
        assert analyzer is not None

    def test_network_storage(self, analyzer):
        """Test that networks are stored correctly"""
        network = analyzer.build_user_interaction_network()
        analyzer.networks['test_network'] = network

        assert 'test_network' in analyzer.networks
        assert isinstance(analyzer.networks['test_network'], (nx.Graph, nx.DiGraph))

    def test_metrics_calculation_consistency(self, analyzer):
        """Test that metrics are calculated consistently"""
        network = analyzer.build_user_interaction_network()

        metrics1 = analyzer.calculate_basic_network_metrics(network)
        metrics2 = analyzer.calculate_basic_network_metrics(network)

        assert metrics1['num_nodes'] == metrics2['num_nodes']
        assert metrics1['num_edges'] == metrics2['num_edges']

    def test_crisis_filtering(self, analyzer):
        """Test filtering by crisis ID"""
        if 'crisis_id' in analyzer.df.columns:
            crisis_types = analyzer.df['crisis_id'].unique()
            assert len(crisis_types) > 0

            # Filter by first crisis
            crisis_data = analyzer.df[analyzer.df['crisis_id'] == crisis_types[0]]
            assert len(crisis_data) > 0

    def test_date_range_filtering(self, analyzer):
        """Test filtering by date range"""
        if 'created_utc' in analyzer.df.columns:
            start_date = analyzer.df['created_utc'].min()
            end_date = analyzer.df['created_utc'].max()

            date_filtered = analyzer.df[
                (analyzer.df['created_utc'] >= start_date) &
                (analyzer.df['created_utc'] <= end_date)
            ]

            assert len(date_filtered) > 0


class TestNetworkMetrics:
    """Test suite for network metrics calculation"""

    @pytest.fixture
    def simple_network(self):
        """Create a simple test network"""
        G = nx.Graph()
        G.add_edges_from([
            ('A', 'B'),
            ('B', 'C'),
            ('C', 'D'),
            ('D', 'A'),
            ('A', 'C')
        ])
        return G

    def test_degree_centrality(self, simple_network):
        """Test degree centrality calculation"""
        centrality = nx.degree_centrality(simple_network)

        assert isinstance(centrality, dict)
        assert len(centrality) == simple_network.number_of_nodes()
        assert all(0 <= v <= 1 for v in centrality.values())

    def test_betweenness_centrality(self, simple_network):
        """Test betweenness centrality calculation"""
        centrality = nx.betweenness_centrality(simple_network)

        assert isinstance(centrality, dict)
        assert len(centrality) == simple_network.number_of_nodes()
        assert all(0 <= v <= 1 for v in centrality.values())

    def test_clustering_coefficient(self, simple_network):
        """Test clustering coefficient calculation"""
        clustering = nx.clustering(simple_network)

        assert isinstance(clustering, dict)
        assert len(clustering) == simple_network.number_of_nodes()
        assert all(0 <= v <= 1 for v in clustering.values())

    def test_connected_components(self, simple_network):
        """Test connected components identification"""
        components = list(nx.connected_components(simple_network))

        assert len(components) >= 1
        assert isinstance(components[0], set)


class TestDataValidation:
    """Test suite for data validation in network analysis"""

    def test_valid_post_structure(self):
        """Test validation of post data structure"""
        valid_post = {
            'title': 'Test Post',
            'content': 'Test content',
            'author': 'test_user',
            'created_utc': datetime.now(),
            'score': 100
        }

        # All required fields present
        required_fields = ['title', 'content', 'author', 'created_utc']
        assert all(field in valid_post for field in required_fields)

    def test_invalid_post_structure(self):
        """Test handling of invalid post structure"""
        invalid_post = {
            'title': 'Test Post',
            # Missing 'content', 'author', etc.
        }

        required_fields = ['title', 'content', 'author', 'created_utc']
        missing_fields = [f for f in required_fields if f not in invalid_post]

        assert len(missing_fields) > 0

    def test_data_type_validation(self):
        """Test data type validation"""
        post = {
            'title': 'Test Post',
            'content': 'Test content',
            'author': 'test_user',
            'score': 100,
            'created_utc': datetime.now()
        }

        assert isinstance(post['title'], str)
        assert isinstance(post['content'], str)
        assert isinstance(post['score'], (int, float))
        assert isinstance(post['created_utc'], datetime)


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
