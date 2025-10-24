"""
Unit tests for Reddit collector modules
"""

import pytest
import pandas as pd
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from collection.working_reddit_collector import WorkingRedditCollector


class TestWorkingRedditCollector:
    """Test suite for WorkingRedditCollector"""

    @pytest.fixture
    def mock_reddit(self):
        """Create mock Reddit instance"""
        mock_reddit = Mock()
        mock_reddit.read_only = True
        return mock_reddit

    @pytest.fixture
    def collector(self, mock_reddit):
        """Create collector instance with mock Reddit"""
        with patch('praw.Reddit', return_value=mock_reddit):
            collector = WorkingRedditCollector(
                client_id='test_id',
                client_secret='test_secret',
                user_agent='test_agent'
            )
            return collector

    def test_collector_initialization(self, collector):
        """Test collector initializes correctly"""
        assert collector is not None
        assert hasattr(collector, 'reddit')

    @patch('praw.Reddit')
    def test_collector_with_credentials(self, mock_reddit_class):
        """Test collector initialization with credentials"""
        collector = WorkingRedditCollector(
            client_id='test_id',
            client_secret='test_secret',
            user_agent='test_agent'
        )

        mock_reddit_class.assert_called_once_with(
            client_id='test_id',
            client_secret='test_secret',
            user_agent='test_agent'
        )

    def test_collect_posts_returns_dataframe(self, collector):
        """Test that collect_posts returns a DataFrame"""
        # Mock subreddit and posts
        mock_post = Mock()
        mock_post.title = "Test Post"
        mock_post.selftext = "Test content"
        mock_post.author.name = "test_author"
        mock_post.subreddit.display_name = "test_subreddit"
        mock_post.created_utc = datetime.now().timestamp()
        mock_post.score = 100
        mock_post.num_comments = 10
        mock_post.upvote_ratio = 0.95
        mock_post.url = "https://reddit.com/test"
        mock_post.id = "test123"
        mock_post.permalink = "/r/test/test123"

        mock_subreddit = Mock()
        mock_subreddit.hot.return_value = [mock_post]

        collector.reddit.subreddit.return_value = mock_subreddit

        # Collect posts
        df = collector.collect_posts(
            subreddit='test',
            limit=1,
            time_filter='week'
        )

        # Assertions
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert 'title' in df.columns
        assert 'content' in df.columns
        assert 'author' in df.columns

    def test_collect_posts_handles_deleted_author(self, collector):
        """Test handling of deleted author"""
        mock_post = Mock()
        mock_post.title = "Test Post"
        mock_post.selftext = "Test content"
        mock_post.author = None  # Deleted author
        mock_post.subreddit.display_name = "test_subreddit"
        mock_post.created_utc = datetime.now().timestamp()
        mock_post.score = 100
        mock_post.num_comments = 10
        mock_post.upvote_ratio = 0.95
        mock_post.url = "https://reddit.com/test"
        mock_post.id = "test123"
        mock_post.permalink = "/r/test/test123"

        mock_subreddit = Mock()
        mock_subreddit.hot.return_value = [mock_post]
        collector.reddit.subreddit.return_value = mock_subreddit

        df = collector.collect_posts(subreddit='test', limit=1)

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert df.iloc[0]['author'] == '[deleted]'

    def test_collect_posts_with_limit(self, collector):
        """Test that limit parameter is respected"""
        mock_posts = []
        for i in range(5):
            mock_post = Mock()
            mock_post.title = f"Test Post {i}"
            mock_post.selftext = f"Test content {i}"
            mock_post.author.name = f"author{i}"
            mock_post.subreddit.display_name = "test_subreddit"
            mock_post.created_utc = datetime.now().timestamp()
            mock_post.score = 100
            mock_post.num_comments = 10
            mock_post.upvote_ratio = 0.95
            mock_post.url = f"https://reddit.com/test{i}"
            mock_post.id = f"test{i}"
            mock_post.permalink = f"/r/test/test{i}"
            mock_posts.append(mock_post)

        mock_subreddit = Mock()
        mock_subreddit.hot.return_value = mock_posts[:3]  # Return only 3

        collector.reddit.subreddit.return_value = mock_subreddit

        df = collector.collect_posts(subreddit='test', limit=3)

        assert len(df) <= 3

    def test_search_posts_returns_dataframe(self, collector):
        """Test that search_posts returns a DataFrame"""
        mock_post = Mock()
        mock_post.title = "Crisis Test Post"
        mock_post.selftext = "Crisis content"
        mock_post.author.name = "test_author"
        mock_post.subreddit.display_name = "test_subreddit"
        mock_post.created_utc = datetime.now().timestamp()
        mock_post.score = 100
        mock_post.num_comments = 10
        mock_post.upvote_ratio = 0.95
        mock_post.url = "https://reddit.com/test"
        mock_post.id = "test123"
        mock_post.permalink = "/r/test/test123"

        mock_subreddit = Mock()
        mock_subreddit.search.return_value = [mock_post]

        collector.reddit.subreddit.return_value = mock_subreddit

        df = collector.search_posts(
            subreddit='test',
            query='crisis',
            limit=1
        )

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_save_to_csv(self, collector, tmp_path):
        """Test saving DataFrame to CSV"""
        # Create test DataFrame
        test_data = {
            'title': ['Test Post'],
            'content': ['Test content'],
            'author': ['test_author'],
            'subreddit': ['test_sub'],
            'created_utc': [datetime.now()],
            'score': [100],
            'num_comments': [10]
        }
        df = pd.DataFrame(test_data)

        # Save to temp file
        output_file = tmp_path / "test_output.csv"
        collector.save_to_csv(df, str(output_file))

        # Check file exists and can be read
        assert output_file.exists()
        loaded_df = pd.read_csv(output_file)
        assert len(loaded_df) == 1
        assert loaded_df.iloc[0]['title'] == 'Test Post'

    def test_empty_collection(self, collector):
        """Test behavior with no posts returned"""
        mock_subreddit = Mock()
        mock_subreddit.hot.return_value = []

        collector.reddit.subreddit.return_value = mock_subreddit

        df = collector.collect_posts(subreddit='test', limit=10)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_exception_handling(self, collector):
        """Test that exceptions are handled gracefully"""
        mock_subreddit = Mock()
        mock_subreddit.hot.side_effect = Exception("API Error")

        collector.reddit.subreddit.return_value = mock_subreddit

        # Should not raise exception
        df = collector.collect_posts(subreddit='test', limit=10)

        # Should return empty DataFrame or handle gracefully
        assert isinstance(df, pd.DataFrame)


class TestRedditCollectorIntegration:
    """Integration tests for Reddit collector"""

    @pytest.mark.integration
    def test_crisis_keywords_collection(self):
        """Test collection with crisis-specific keywords"""
        # This would test with actual Reddit API in integration environment
        # For now, we'll skip in unit tests
        pytest.skip("Requires actual Reddit API credentials")

    @pytest.mark.integration
    def test_multiple_subreddit_collection(self):
        """Test collecting from multiple subreddits"""
        pytest.skip("Requires actual Reddit API credentials")

    @pytest.mark.integration
    def test_date_range_filtering(self):
        """Test filtering posts by date range"""
        pytest.skip("Requires actual Reddit API credentials")


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
