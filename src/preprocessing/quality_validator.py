"""
Data Quality Validator for Crisis Network Analysis
Validates data quality and provides quality metrics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging
import re
from collections import Counter

logger = logging.getLogger(__name__)


class QualityValidator:
    """
    Validates data quality for crisis social media datasets

    Features:
    - Completeness checks
    - Consistency validation
    - Relevance scoring
    - Temporal coverage analysis
    - Language detection
    - Spam detection
    """

    def __init__(self):
        """Initialize the quality validator"""
        self.validation_results = {}
        self.quality_metrics = {}

    def validate_dataset(self, df: pd.DataFrame, crisis_config: Optional[Dict] = None) -> Dict:
        """
        Comprehensive dataset validation

        Args:
            df: Input DataFrame
            crisis_config: Optional crisis configuration for relevance checking

        Returns:
            Dictionary with validation results
        """
        logger.info(f"Starting quality validation on {len(df)} rows")

        results = {
            'completeness': self._check_completeness(df),
            'consistency': self._check_consistency(df),
            'temporal_coverage': self._check_temporal_coverage(df),
            'content_quality': self._check_content_quality(df),
            'data_distribution': self._check_data_distribution(df),
            'overall_score': 0.0
        }

        # Add relevance check if crisis config provided
        if crisis_config:
            results['relevance'] = self._check_relevance(df, crisis_config)

        # Calculate overall quality score
        results['overall_score'] = self._calculate_overall_score(results)

        self.validation_results = results
        logger.info(f"Validation complete. Overall quality score: {results['overall_score']:.2f}/100")

        return results

    def _check_completeness(self, df: pd.DataFrame) -> Dict:
        """
        Check data completeness

        Returns:
            Dictionary with completeness metrics
        """
        required_columns = ['title', 'content', 'author', 'created_utc', 'score']
        optional_columns = ['subreddit', 'num_comments', 'upvote_ratio', 'url']

        completeness = {
            'total_rows': len(df),
            'required_columns_present': [],
            'missing_required_columns': [],
            'optional_columns_present': [],
            'column_completeness': {},
            'score': 0.0
        }

        # Check required columns
        for col in required_columns:
            if col in df.columns:
                completeness['required_columns_present'].append(col)
                missing_pct = (df[col].isna().sum() / len(df)) * 100
                completeness['column_completeness'][col] = 100 - missing_pct
            else:
                completeness['missing_required_columns'].append(col)
                completeness['column_completeness'][col] = 0

        # Check optional columns
        for col in optional_columns:
            if col in df.columns:
                completeness['optional_columns_present'].append(col)
                missing_pct = (df[col].isna().sum() / len(df)) * 100
                completeness['column_completeness'][col] = 100 - missing_pct

        # Calculate completeness score
        if required_columns:
            avg_completeness = np.mean([
                completeness['column_completeness'].get(col, 0)
                for col in required_columns
            ])
            completeness['score'] = avg_completeness

        return completeness

    def _check_consistency(self, df: pd.DataFrame) -> Dict:
        """
        Check data consistency

        Returns:
            Dictionary with consistency metrics
        """
        consistency = {
            'timestamp_issues': 0,
            'negative_scores': 0,
            'invalid_ratios': 0,
            'empty_content': 0,
            'score': 100.0
        }

        # Check timestamp consistency
        if 'created_utc' in df.columns:
            try:
                timestamps = pd.to_datetime(df['created_utc'])
                future_dates = (timestamps > pd.Timestamp.now()).sum()
                consistency['timestamp_issues'] = int(future_dates)
            except Exception as e:
                logger.warning(f"Could not validate timestamps: {e}")

        # Check for negative scores
        if 'score' in df.columns:
            consistency['negative_scores'] = int((df['score'] < 0).sum())

        # Check for invalid upvote ratios
        if 'upvote_ratio' in df.columns:
            invalid_ratios = (
                (df['upvote_ratio'] < 0) | (df['upvote_ratio'] > 1)
            ).sum()
            consistency['invalid_ratios'] = int(invalid_ratios)

        # Check for empty content
        if 'content' in df.columns:
            empty = df['content'].str.strip().str.len() == 0
            consistency['empty_content'] = int(empty.sum())

        # Calculate consistency score
        total_issues = sum([
            consistency['timestamp_issues'],
            consistency['negative_scores'],
            consistency['invalid_ratios'],
            consistency['empty_content']
        ])

        issue_rate = (total_issues / len(df)) * 100
        consistency['score'] = max(0, 100 - issue_rate)

        return consistency

    def _check_temporal_coverage(self, df: pd.DataFrame) -> Dict:
        """
        Check temporal coverage of the dataset

        Returns:
            Dictionary with temporal metrics
        """
        temporal = {
            'start_date': None,
            'end_date': None,
            'duration_days': 0,
            'posts_per_day': 0,
            'time_gaps': [],
            'coverage_score': 0.0
        }

        if 'created_utc' not in df.columns:
            return temporal

        try:
            timestamps = pd.to_datetime(df['created_utc'])

            temporal['start_date'] = timestamps.min().strftime('%Y-%m-%d')
            temporal['end_date'] = timestamps.max().strftime('%Y-%m-%d')

            duration = (timestamps.max() - timestamps.min()).days
            temporal['duration_days'] = duration

            if duration > 0:
                temporal['posts_per_day'] = len(df) / duration

            # Check for time gaps (days with no posts)
            date_range = pd.date_range(
                start=timestamps.min(),
                end=timestamps.max(),
                freq='D'
            )

            posts_by_date = timestamps.dt.date.value_counts()
            missing_dates = [
                date.strftime('%Y-%m-%d')
                for date in date_range
                if date.date() not in posts_by_date.index
            ]

            temporal['time_gaps'] = missing_dates[:10]  # Show first 10 gaps
            temporal['gap_count'] = len(missing_dates)

            # Calculate coverage score
            coverage_rate = (1 - len(missing_dates) / len(date_range)) * 100
            temporal['coverage_score'] = coverage_rate

        except Exception as e:
            logger.warning(f"Could not analyze temporal coverage: {e}")

        return temporal

    def _check_content_quality(self, df: pd.DataFrame) -> Dict:
        """
        Check content quality metrics

        Returns:
            Dictionary with content quality metrics
        """
        quality = {
            'avg_content_length': 0,
            'avg_title_length': 0,
            'too_short_count': 0,
            'too_long_count': 0,
            'spam_indicators': 0,
            'quality_score': 0.0
        }

        # Content length analysis
        if 'content' in df.columns:
            lengths = df['content'].str.len()
            quality['avg_content_length'] = float(lengths.mean())
            quality['too_short_count'] = int((lengths < 20).sum())
            quality['too_long_count'] = int((lengths > 10000).sum())

            # Detect spam indicators
            spam_patterns = [
                r'(?i)(buy|sale|discount|offer|limited time)',
                r'(?i)(click here|visit now|follow link)',
                r'http[s]?://.*\s+http[s]?://.*\s+http[s]://',  # Multiple links
            ]

            spam_count = 0
            for pattern in spam_patterns:
                spam_count += df['content'].str.contains(pattern, na=False, regex=True).sum()

            quality['spam_indicators'] = int(spam_count)

        # Title length analysis
        if 'title' in df.columns:
            title_lengths = df['title'].str.len()
            quality['avg_title_length'] = float(title_lengths.mean())

        # Calculate quality score
        issues_pct = (
            quality['too_short_count'] +
            quality['too_long_count'] +
            quality['spam_indicators']
        ) / len(df) * 100

        quality['quality_score'] = max(0, 100 - issues_pct)

        return quality

    def _check_data_distribution(self, df: pd.DataFrame) -> Dict:
        """
        Check data distribution across different dimensions

        Returns:
            Dictionary with distribution metrics
        """
        distribution = {
            'authors': {},
            'subreddits': {},
            'time_of_day': {},
            'balance_score': 0.0
        }

        # Author distribution
        if 'author' in df.columns:
            author_counts = df['author'].value_counts()
            distribution['authors'] = {
                'unique_count': len(author_counts),
                'top_author_percentage': (author_counts.iloc[0] / len(df)) * 100 if len(author_counts) > 0 else 0,
                'median_posts_per_author': float(author_counts.median())
            }

        # Subreddit distribution
        if 'subreddit' in df.columns:
            subreddit_counts = df['subreddit'].value_counts()
            distribution['subreddits'] = {
                'unique_count': len(subreddit_counts),
                'top_subreddit_percentage': (subreddit_counts.iloc[0] / len(df)) * 100 if len(subreddit_counts) > 0 else 0,
                'coverage': list(subreddit_counts.head(10).to_dict().items())
            }

        # Time of day distribution
        if 'created_utc' in df.columns:
            try:
                timestamps = pd.to_datetime(df['created_utc'])
                hour_counts = timestamps.dt.hour.value_counts()
                distribution['time_of_day'] = {
                    'peak_hour': int(hour_counts.idxmax()),
                    'lowest_hour': int(hour_counts.idxmin()),
                    'variation': float(hour_counts.std())
                }
            except Exception as e:
                logger.warning(f"Could not analyze time distribution: {e}")

        # Calculate balance score (lower concentration = better)
        concentration_scores = []

        if 'authors' in distribution and 'top_author_percentage' in distribution['authors']:
            concentration_scores.append(100 - distribution['authors']['top_author_percentage'])

        if 'subreddits' in distribution and 'top_subreddit_percentage' in distribution['subreddits']:
            concentration_scores.append(100 - distribution['subreddits']['top_subreddit_percentage'])

        if concentration_scores:
            distribution['balance_score'] = np.mean(concentration_scores)

        return distribution

    def _check_relevance(self, df: pd.DataFrame, crisis_config: Dict) -> Dict:
        """
        Check relevance to crisis based on keywords

        Args:
            df: Input DataFrame
            crisis_config: Crisis configuration with keywords

        Returns:
            Dictionary with relevance metrics
        """
        relevance = {
            'keyword_matches': 0,
            'relevance_rate': 0.0,
            'score': 0.0
        }

        if 'content' not in df.columns:
            return relevance

        # Extract keywords from crisis config
        keywords = []
        if 'keywords' in crisis_config:
            for key, values in crisis_config['keywords'].items():
                if isinstance(values, list):
                    keywords.extend(values)

        if not keywords:
            return relevance

        # Check for keyword matches
        pattern = '|'.join([re.escape(kw.lower()) for kw in keywords])

        matches = df['content'].str.lower().str.contains(pattern, na=False, regex=True)
        relevance['keyword_matches'] = int(matches.sum())
        relevance['relevance_rate'] = (matches.sum() / len(df)) * 100
        relevance['score'] = relevance['relevance_rate']

        return relevance

    def _calculate_overall_score(self, results: Dict) -> float:
        """
        Calculate overall quality score

        Args:
            results: Validation results dictionary

        Returns:
            Overall quality score (0-100)
        """
        scores = []
        weights = []

        # Completeness (30% weight)
        if 'completeness' in results and 'score' in results['completeness']:
            scores.append(results['completeness']['score'])
            weights.append(0.30)

        # Consistency (25% weight)
        if 'consistency' in results and 'score' in results['consistency']:
            scores.append(results['consistency']['score'])
            weights.append(0.25)

        # Content Quality (25% weight)
        if 'content_quality' in results and 'quality_score' in results['content_quality']:
            scores.append(results['content_quality']['quality_score'])
            weights.append(0.25)

        # Temporal Coverage (10% weight)
        if 'temporal_coverage' in results and 'coverage_score' in results['temporal_coverage']:
            scores.append(results['temporal_coverage']['coverage_score'])
            weights.append(0.10)

        # Distribution Balance (10% weight)
        if 'data_distribution' in results and 'balance_score' in results['data_distribution']:
            scores.append(results['data_distribution']['balance_score'])
            weights.append(0.10)

        # Calculate weighted average
        if scores and weights:
            # Normalize weights
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights]

            overall_score = sum(s * w for s, w in zip(scores, normalized_weights))
            return overall_score

        return 0.0

    def generate_quality_report(self) -> str:
        """
        Generate a human-readable quality report

        Returns:
            Formatted quality report string
        """
        if not self.validation_results:
            return "No validation results available. Run validate_dataset() first."

        report = []
        report.append("=" * 70)
        report.append("DATA QUALITY VALIDATION REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Overall Score
        overall = self.validation_results.get('overall_score', 0)
        report.append(f"OVERALL QUALITY SCORE: {overall:.2f}/100")
        report.append("")

        # Quality Rating
        if overall >= 90:
            rating = "EXCELLENT"
        elif overall >= 75:
            rating = "GOOD"
        elif overall >= 60:
            rating = "ACCEPTABLE"
        elif overall >= 40:
            rating = "POOR"
        else:
            rating = "VERY POOR"

        report.append(f"Quality Rating: {rating}")
        report.append("")
        report.append("-" * 70)

        # Completeness
        if 'completeness' in self.validation_results:
            comp = self.validation_results['completeness']
            report.append("COMPLETENESS:")
            report.append(f"  Score: {comp.get('score', 0):.2f}/100")
            report.append(f"  Total Rows: {comp.get('total_rows', 0)}")
            report.append(f"  Required Columns Present: {len(comp.get('required_columns_present', []))}")
            if comp.get('missing_required_columns'):
                report.append(f"  ⚠️  Missing Required: {comp['missing_required_columns']}")
            report.append("")

        # Consistency
        if 'consistency' in self.validation_results:
            cons = self.validation_results['consistency']
            report.append("CONSISTENCY:")
            report.append(f"  Score: {cons.get('score', 0):.2f}/100")
            report.append(f"  Timestamp Issues: {cons.get('timestamp_issues', 0)}")
            report.append(f"  Negative Scores: {cons.get('negative_scores', 0)}")
            report.append(f"  Invalid Ratios: {cons.get('invalid_ratios', 0)}")
            report.append(f"  Empty Content: {cons.get('empty_content', 0)}")
            report.append("")

        # Temporal Coverage
        if 'temporal_coverage' in self.validation_results:
            temp = self.validation_results['temporal_coverage']
            report.append("TEMPORAL COVERAGE:")
            report.append(f"  Score: {temp.get('coverage_score', 0):.2f}/100")
            report.append(f"  Date Range: {temp.get('start_date')} to {temp.get('end_date')}")
            report.append(f"  Duration: {temp.get('duration_days', 0)} days")
            report.append(f"  Posts per Day: {temp.get('posts_per_day', 0):.1f}")
            if temp.get('gap_count', 0) > 0:
                report.append(f"  ⚠️  Time Gaps: {temp['gap_count']} days with no posts")
            report.append("")

        # Content Quality
        if 'content_quality' in self.validation_results:
            qual = self.validation_results['content_quality']
            report.append("CONTENT QUALITY:")
            report.append(f"  Score: {qual.get('quality_score', 0):.2f}/100")
            report.append(f"  Avg Content Length: {qual.get('avg_content_length', 0):.0f} chars")
            report.append(f"  Too Short: {qual.get('too_short_count', 0)}")
            report.append(f"  Too Long: {qual.get('too_long_count', 0)}")
            if qual.get('spam_indicators', 0) > 0:
                report.append(f"  ⚠️  Spam Indicators: {qual['spam_indicators']}")
            report.append("")

        report.append("=" * 70)

        return "\n".join(report)

    def save_validation_report(self, output_path: str):
        """Save validation report to file"""
        report = self.generate_quality_report()

        with open(output_path, 'w') as f:
            f.write(report)

        logger.info(f"Validation report saved to {output_path}")
