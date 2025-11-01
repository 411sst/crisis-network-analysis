"""
Unit tests for preprocessing modules
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from preprocessing.data_cleaner import DataCleaner
from preprocessing.quality_validator import QualityValidator


class TestDataCleaner:
    """Test suite for DataCleaner"""

    @pytest.fixture
    def sample_data(self):
        """Create sample data with quality issues"""
        data = {
            'title': [
                'Test Post 1',
                'Test Post 2',
                'Test Post 1',  # Duplicate
                '[deleted]',     # Deleted
                'Test Post 5',
                'Short',         # Too short content below
            ],
            'content': [
                'This is good content about the crisis',
                'More good content here',
                'This is good content about the crisis',  # Duplicate
                '[deleted]',
                'Test content' * 100,  # Very long
                'Too short',           # Too short
            ],
            'author': [
                'user1',
                'user2',
                'user1',
                '[deleted]',
                'AutoModerator',  # Bot
                'user3'
            ],
            'created_utc': [
                datetime.now() - timedelta(days=5),
                datetime.now() - timedelta(days=4),
                datetime.now() - timedelta(days=5),  # Duplicate
                datetime.now() - timedelta(days=3),
                datetime.now() - timedelta(days=2),
                datetime.now() - timedelta(days=1)
            ],
            'score': [100, 200, 100, 0, 150, 50],
            'subreddit': ['test', 'test', 'test', 'test', 'test', 'test']
        }
        return pd.DataFrame(data)

    @pytest.fixture
    def cleaner(self):
        """Create DataCleaner instance"""
        return DataCleaner()

    def test_cleaner_initialization(self, cleaner):
        """Test cleaner initializes correctly"""
        assert cleaner is not None
        assert hasattr(cleaner, 'config')
        assert hasattr(cleaner, 'cleaning_stats')

    def test_duplicate_removal(self, cleaner, sample_data):
        """Test removal of duplicate posts"""
        initial_len = len(sample_data)
        cleaned = cleaner._remove_duplicates(sample_data)

        assert len(cleaned) < initial_len
        assert cleaner.cleaning_stats['duplicates_removed'] > 0

    def test_text_cleaning(self, cleaner, sample_data):
        """Test text cleaning functionality"""
        cleaned = cleaner._clean_text_columns(sample_data)

        # Check that whitespace is normalized
        for content in cleaned['content']:
            if isinstance(content, str):
                assert '  ' not in content  # No double spaces
                assert content == content.strip()  # No leading/trailing whitespace

    def test_clean_text_function(self, cleaner):
        """Test individual text cleaning"""
        # Test with extra whitespace
        text = "Test   content   with   spaces"
        cleaned = cleaner._clean_text(text)
        assert '  ' not in cleaned

        # Test with special characters
        text = "Test\x00content"
        cleaned = cleaner._clean_text(text)
        assert '\x00' not in cleaned

    def test_missing_value_handling(self, cleaner):
        """Test handling of missing values"""
        data = pd.DataFrame({
            'title': ['Test', None, 'Test3'],
            'content': ['Content', 'Content2', None],
            'score': [100, None, 50]
        })

        cleaned = cleaner._handle_missing_values(data)

        # Text fields should be filled with empty string
        assert cleaned['title'].notna().all()
        assert cleaned['content'].notna().all()

        # Numeric fields should be filled with 0
        assert cleaned['score'].notna().all()

    def test_deleted_content_removal(self, cleaner, sample_data):
        """Test removal of deleted/removed content"""
        initial_len = len(sample_data)
        cleaned = cleaner._remove_deleted_content(sample_data)

        assert len(cleaned) < initial_len
        assert '[deleted]' not in cleaned['content'].values
        assert '[deleted]' not in cleaned['author'].values

    def test_bot_removal(self, cleaner, sample_data):
        """Test removal of bot content"""
        initial_len = len(sample_data)
        cleaned = cleaner._remove_bot_content(sample_data)

        assert len(cleaned) < initial_len
        # Check that AutoModerator is removed
        assert 'AutoModerator' not in cleaned['author'].str.lower().values

    def test_content_length_validation(self, cleaner, sample_data):
        """Test content length validation"""
        initial_len = len(sample_data)
        cleaned = cleaner._validate_content_length(sample_data)

        assert len(cleaned) <= initial_len
        # All remaining content should be within limits
        for content in cleaned['content']:
            length = len(content)
            assert length >= cleaner.config['min_content_length']
            assert length <= cleaner.config['max_content_length']

    def test_full_cleaning_pipeline(self, cleaner, sample_data):
        """Test complete cleaning pipeline"""
        initial_len = len(sample_data)
        cleaned = cleaner.clean_dataset(sample_data)

        assert len(cleaned) < initial_len
        assert cleaner.cleaning_stats['initial_rows'] == initial_len
        assert cleaner.cleaning_stats['final_rows'] == len(cleaned)

    def test_cleaning_report_generation(self, cleaner, sample_data):
        """Test cleaning report generation"""
        cleaner.clean_dataset(sample_data)
        report = cleaner.get_cleaning_report()

        assert isinstance(report, dict)
        assert 'initial_rows' in report
        assert 'final_rows' in report
        assert 'rows_removed' in report
        assert 'retention_rate' in report

    def test_custom_config(self):
        """Test cleaner with custom configuration"""
        custom_config = {
            'remove_duplicates': True,
            'min_content_length': 50,
            'max_content_length': 1000
        }

        cleaner = DataCleaner(config=custom_config)

        assert cleaner.config['min_content_length'] == 50
        assert cleaner.config['max_content_length'] == 1000


class TestQualityValidator:
    """Test suite for QualityValidator"""

    @pytest.fixture
    def sample_data(self):
        """Create sample data for validation"""
        data = {
            'title': ['Post ' + str(i) for i in range(100)],
            'content': ['Content ' * 20 + str(i) for i in range(100)],
            'author': [f'user{i % 20}' for i in range(100)],
            'subreddit': [f'sub{i % 5}' for i in range(100)],
            'created_utc': [
                datetime.now() - timedelta(days=i // 10)
                for i in range(100)
            ],
            'score': np.random.randint(0, 1000, 100),
            'num_comments': np.random.randint(0, 100, 100),
            'upvote_ratio': np.random.uniform(0.5, 1.0, 100)
        }
        return pd.DataFrame(data)

    @pytest.fixture
    def validator(self):
        """Create QualityValidator instance"""
        return QualityValidator()

    def test_validator_initialization(self, validator):
        """Test validator initializes correctly"""
        assert validator is not None
        assert hasattr(validator, 'validation_results')
        assert hasattr(validator, 'quality_metrics')

    def test_completeness_check(self, validator, sample_data):
        """Test completeness checking"""
        completeness = validator._check_completeness(sample_data)

        assert isinstance(completeness, dict)
        assert 'score' in completeness
        assert 'required_columns_present' in completeness
        assert 'column_completeness' in completeness
        assert completeness['score'] >= 0
        assert completeness['score'] <= 100

    def test_consistency_check(self, validator, sample_data):
        """Test consistency checking"""
        consistency = validator._check_consistency(sample_data)

        assert isinstance(consistency, dict)
        assert 'score' in consistency
        assert 'timestamp_issues' in consistency
        assert consistency['score'] >= 0
        assert consistency['score'] <= 100

    def test_temporal_coverage_check(self, validator, sample_data):
        """Test temporal coverage analysis"""
        temporal = validator._check_temporal_coverage(sample_data)

        assert isinstance(temporal, dict)
        assert 'start_date' in temporal
        assert 'end_date' in temporal
        assert 'duration_days' in temporal
        assert temporal['duration_days'] >= 0

    def test_content_quality_check(self, validator, sample_data):
        """Test content quality checking"""
        quality = validator._check_content_quality(sample_data)

        assert isinstance(quality, dict)
        assert 'quality_score' in quality
        assert 'avg_content_length' in quality
        assert quality['quality_score'] >= 0
        assert quality['quality_score'] <= 100

    def test_data_distribution_check(self, validator, sample_data):
        """Test data distribution analysis"""
        distribution = validator._check_data_distribution(sample_data)

        assert isinstance(distribution, dict)
        assert 'authors' in distribution
        assert 'subreddits' in distribution

    def test_full_validation(self, validator, sample_data):
        """Test full validation pipeline"""
        results = validator.validate_dataset(sample_data)

        assert isinstance(results, dict)
        assert 'completeness' in results
        assert 'consistency' in results
        assert 'overall_score' in results
        assert results['overall_score'] >= 0
        assert results['overall_score'] <= 100

    def test_relevance_check(self, validator, sample_data):
        """Test relevance checking with crisis config"""
        crisis_config = {
            'keywords': {
                'primary': ['crisis', 'emergency', 'disaster'],
                'secondary': ['help', 'rescue', 'evacuation']
            }
        }

        relevance = validator._check_relevance(sample_data, crisis_config)

        assert isinstance(relevance, dict)
        assert 'keyword_matches' in relevance
        assert 'relevance_rate' in relevance
        assert 'score' in relevance

    def test_quality_report_generation(self, validator, sample_data):
        """Test quality report generation"""
        validator.validate_dataset(sample_data)
        report = validator.generate_quality_report()

        assert isinstance(report, str)
        assert 'OVERALL QUALITY SCORE' in report
        assert 'COMPLETENESS' in report
        assert 'CONSISTENCY' in report

    def test_overall_score_calculation(self, validator):
        """Test overall score calculation"""
        results = {
            'completeness': {'score': 90},
            'consistency': {'score': 85},
            'content_quality': {'quality_score': 80},
            'temporal_coverage': {'coverage_score': 75},
            'data_distribution': {'balance_score': 70}
        }

        score = validator._calculate_overall_score(results)

        assert isinstance(score, float)
        assert 0 <= score <= 100

    def test_empty_dataframe_validation(self, validator):
        """Test validation of empty DataFrame"""
        empty_df = pd.DataFrame(columns=['title', 'content', 'author'])
        results = validator.validate_dataset(empty_df)

        assert isinstance(results, dict)
        assert 'overall_score' in results

    def test_incomplete_dataframe_validation(self, validator):
        """Test validation of incomplete DataFrame"""
        incomplete_df = pd.DataFrame({
            'title': ['Test'],
            # Missing other required columns
        })

        results = validator.validate_dataset(incomplete_df)

        assert isinstance(results, dict)
        assert results['completeness']['score'] < 100


class TestPreprocessingIntegration:
    """Integration tests for preprocessing pipeline"""

    @pytest.fixture
    def messy_data(self):
        """Create messy data that needs both cleaning and validation"""
        data = {
            'title': ['Post ' + str(i) if i % 3 != 0 else None for i in range(50)],
            'content': [
                'Content ' * 10 if i % 5 != 0 else '[deleted]'
                for i in range(50)
            ],
            'author': [
                f'user{i}' if i % 7 != 0 else 'AutoModerator'
                for i in range(50)
            ],
            'created_utc': [datetime.now() - timedelta(days=i) for i in range(50)],
            'score': [i * 10 if i % 4 != 0 else None for i in range(50)]
        }
        return pd.DataFrame(data)

    def test_clean_then_validate_pipeline(self, messy_data):
        """Test cleaning followed by validation"""
        # Clean first
        cleaner = DataCleaner()
        cleaned = cleaner.clean_dataset(messy_data)

        assert len(cleaned) < len(messy_data)

        # Then validate
        validator = QualityValidator()
        results = validator.validate_dataset(cleaned)

        # Cleaned data should have better quality score
        assert results['overall_score'] > 0
        assert results['consistency']['score'] > 80  # Should be very consistent after cleaning


# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "preprocessing: mark test as preprocessing test"
    )
