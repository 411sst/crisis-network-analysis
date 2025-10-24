"""
Data Cleaning Module for Crisis Network Analysis
Provides comprehensive data cleaning and preprocessing functionality
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DataCleaner:
    """
    Comprehensive data cleaning for crisis social media data

    Features:
    - Text cleaning and normalization
    - Duplicate detection and removal
    - Missing value handling
    - Data type validation
    - Outlier detection
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the data cleaner

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or self._default_config()
        self.cleaning_stats = {
            'initial_rows': 0,
            'final_rows': 0,
            'duplicates_removed': 0,
            'invalid_rows_removed': 0,
            'missing_values_filled': 0,
            'text_cleaned': 0
        }

    def _default_config(self) -> Dict:
        """Default cleaning configuration"""
        return {
            'remove_duplicates': True,
            'remove_deleted': True,
            'remove_bots': True,
            'min_content_length': 10,
            'max_content_length': 50000,
            'clean_text': True,
            'handle_missing': True,
            'remove_outliers': True
        }

    def clean_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Main cleaning pipeline for crisis data

        Args:
            df: Input DataFrame

        Returns:
            Cleaned DataFrame
        """
        logger.info(f"Starting data cleaning on {len(df)} rows")
        self.cleaning_stats['initial_rows'] = len(df)

        # Create a copy to avoid modifying original
        df_clean = df.copy()

        # 1. Remove duplicates
        if self.config['remove_duplicates']:
            df_clean = self._remove_duplicates(df_clean)

        # 2. Clean text content
        if self.config['clean_text']:
            df_clean = self._clean_text_columns(df_clean)

        # 3. Handle missing values
        if self.config['handle_missing']:
            df_clean = self._handle_missing_values(df_clean)

        # 4. Remove deleted/removed content
        if self.config['remove_deleted']:
            df_clean = self._remove_deleted_content(df_clean)

        # 5. Remove bot accounts
        if self.config['remove_bots']:
            df_clean = self._remove_bot_content(df_clean)

        # 6. Validate content length
        df_clean = self._validate_content_length(df_clean)

        # 7. Remove outliers
        if self.config['remove_outliers']:
            df_clean = self._remove_statistical_outliers(df_clean)

        # 8. Standardize data types
        df_clean = self._standardize_data_types(df_clean)

        self.cleaning_stats['final_rows'] = len(df_clean)
        logger.info(f"Cleaning complete: {len(df_clean)} rows remaining")

        return df_clean

    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate posts based on content and author"""
        initial_len = len(df)

        # Check for exact duplicates
        df = df.drop_duplicates(subset=['title', 'content', 'author'], keep='first')

        # Check for near-duplicates based on content similarity
        if 'content' in df.columns:
            df = df.drop_duplicates(subset=['content'], keep='first')

        duplicates_removed = initial_len - len(df)
        self.cleaning_stats['duplicates_removed'] += duplicates_removed

        if duplicates_removed > 0:
            logger.info(f"Removed {duplicates_removed} duplicate rows")

        return df

    def _clean_text_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean text in title and content columns"""
        text_columns = ['title', 'content']

        for col in text_columns:
            if col in df.columns:
                # Remove extra whitespace
                df[col] = df[col].apply(lambda x: self._clean_text(x) if isinstance(x, str) else x)
                self.cleaning_stats['text_cleaned'] += len(df)

        logger.info(f"Cleaned text in columns: {text_columns}")
        return df

    def _clean_text(self, text: str) -> str:
        """
        Clean individual text string

        Args:
            text: Input text

        Returns:
            Cleaned text
        """
        if not isinstance(text, str):
            return text

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters that might cause issues
        text = text.replace('\x00', '')

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values appropriately"""

        # Fill missing text with empty string
        text_columns = ['title', 'content', 'author', 'subreddit']
        for col in text_columns:
            if col in df.columns:
                missing_count = df[col].isna().sum()
                if missing_count > 0:
                    df[col] = df[col].fillna('')
                    self.cleaning_stats['missing_values_filled'] += missing_count

        # Fill missing numeric values with 0
        numeric_columns = ['score', 'num_comments', 'upvote_ratio']
        for col in numeric_columns:
            if col in df.columns:
                missing_count = df[col].isna().sum()
                if missing_count > 0:
                    df[col] = df[col].fillna(0)
                    self.cleaning_stats['missing_values_filled'] += missing_count

        logger.info(f"Handled missing values: {self.cleaning_stats['missing_values_filled']}")
        return df

    def _remove_deleted_content(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove deleted or removed posts"""
        initial_len = len(df)

        # Common indicators of deleted/removed content
        deleted_indicators = [
            '[deleted]',
            '[removed]',
            '[removed by moderator]',
            '[deleted by user]'
        ]

        # Filter out deleted content
        if 'content' in df.columns:
            mask = ~df['content'].str.lower().isin([x.lower() for x in deleted_indicators])
            df = df[mask]

        if 'author' in df.columns:
            mask = ~df['author'].str.lower().isin(['[deleted]', '[removed]'])
            df = df[mask]

        removed = initial_len - len(df)
        if removed > 0:
            self.cleaning_stats['invalid_rows_removed'] += removed
            logger.info(f"Removed {removed} deleted/removed posts")

        return df

    def _remove_bot_content(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove content from known bot accounts"""
        if 'author' not in df.columns:
            return df

        initial_len = len(df)

        # Common bot username patterns
        bot_patterns = [
            r'.*bot$',
            r'bot.*',
            r'auto.*',
            r'.*moderator.*'
        ]

        # Create mask for non-bot content
        mask = pd.Series([True] * len(df))
        for pattern in bot_patterns:
            mask &= ~df['author'].str.lower().str.match(pattern, na=False)

        df = df[mask]

        removed = initial_len - len(df)
        if removed > 0:
            self.cleaning_stats['invalid_rows_removed'] += removed
            logger.info(f"Removed {removed} bot posts")

        return df

    def _validate_content_length(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove posts with invalid content length"""
        if 'content' not in df.columns:
            return df

        initial_len = len(df)

        # Calculate content length
        df['content_length'] = df['content'].str.len()

        # Filter by length constraints
        df = df[
            (df['content_length'] >= self.config['min_content_length']) &
            (df['content_length'] <= self.config['max_content_length'])
        ]

        removed = initial_len - len(df)
        if removed > 0:
            self.cleaning_stats['invalid_rows_removed'] += removed
            logger.info(f"Removed {removed} posts with invalid content length")

        return df

    def _remove_statistical_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove statistical outliers from numeric columns"""
        numeric_columns = ['score', 'num_comments']

        initial_len = len(df)

        for col in numeric_columns:
            if col in df.columns:
                # Use IQR method for outlier detection
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1

                # Define outlier boundaries
                lower_bound = Q1 - 3 * IQR
                upper_bound = Q3 + 3 * IQR

                # Filter outliers
                df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]

        removed = initial_len - len(df)
        if removed > 0:
            self.cleaning_stats['invalid_rows_removed'] += removed
            logger.info(f"Removed {removed} statistical outliers")

        return df

    def _standardize_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize data types for all columns"""

        # Convert timestamps to datetime
        timestamp_columns = ['created_utc', 'timestamp']
        for col in timestamp_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception as e:
                    logger.warning(f"Could not convert {col} to datetime: {e}")

        # Ensure numeric columns are numeric
        numeric_columns = ['score', 'num_comments', 'upvote_ratio']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Ensure text columns are strings
        text_columns = ['title', 'content', 'author', 'subreddit']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str)

        logger.info("Standardized data types")
        return df

    def get_cleaning_report(self) -> Dict:
        """
        Generate a cleaning report

        Returns:
            Dictionary with cleaning statistics
        """
        report = self.cleaning_stats.copy()
        report['rows_removed'] = report['initial_rows'] - report['final_rows']
        report['retention_rate'] = (
            report['final_rows'] / report['initial_rows'] * 100
            if report['initial_rows'] > 0 else 0
        )

        return report

    def save_cleaning_report(self, output_path: Union[str, Path]):
        """Save cleaning report to file"""
        report = self.get_cleaning_report()

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write("Data Cleaning Report\n")
            f.write("=" * 50 + "\n\n")
            for key, value in report.items():
                f.write(f"{key}: {value}\n")

        logger.info(f"Cleaning report saved to {output_path}")
