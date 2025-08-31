"""
Reddit Crisis Data Collector for Week 1 Initial Data Sample
Collects 2k-5k posts from crisis-relevant subreddits as required by roadmap
"""

import praw
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import time
import json
from pathlib import Path

from src.utils.config_loader import get_config
from src.utils.logger import get_logger

class RedditCrisisCollector:
    """Collect crisis data from Reddit for initial sample (Week 1 deliverable)"""

    def __init__(self):
        """Initialize the Reddit crisis data collector"""
        self.config = get_config()
        self.logger = get_logger('reddit_collector')

        # Initialize Reddit API
        api_keys = self.config.get_api_keys()['reddit']
        self.reddit = praw.Reddit(
            client_id=api_keys['client_id'],
            client_secret=api_keys['client_secret'],
            user_agent=api_keys['user_agent']
        )

        # Verify connection
        try:
            self.reddit.user.me()
            self.logger.info("Reddit API connection successful")
        except:
            self.logger.info("Reddit API in read-only mode (expected)")

        # Data storage paths
        self.raw_data_dir = Path('data/raw')
        self.raw_data_dir.mkdir(exist_ok=True)

    def collect_crisis_sample_data(self,
                                 crisis_id: str,
                                 target_posts: int = 1000,
                                 max_posts_per_subreddit: int = 200) -> pd.DataFrame:
        """
        Collect sample data for a specific crisis (Week 1 requirement)

        Args:
            crisis_id (str): Crisis event identifier
            target_posts (int): Target number of posts to collect
            max_posts_per_subreddit (int): Maximum posts per subreddit

        Returns:
            pd.DataFrame: Collected posts data
        """
        start_time = datetime.now()
        self.logger.info(f"Starting data collection for crisis: {crisis_id}")

        # Get crisis configuration
        crisis_config = self.config.get_crisis_event_config(crisis_id)
        subreddits = self.config.get_reddit_subreddits(crisis_id)
        keywords = self.config.get_crisis_keywords(crisis_id, 'primary')

        # Combine primary and secondary keywords
        all_keywords = keywords + self.config.get_crisis_keywords(crisis_id, 'secondary')

        collected_posts = []
        posts_collected = 0

        self.logger.info(f"Target posts: {target_posts}, Subreddits: {len(subreddits)}")

        # Collect from each subreddit
        for subreddit_name in subreddits:
            if posts_collected >= target_posts:
                break

            try:
                self.logger.info(f"Collecting from r/{subreddit_name}")
                subreddit = self.reddit.subreddit(subreddit_name)

                # Search for crisis-related posts
                subreddit_posts = self._search_subreddit_for_crisis(
                    subreddit,
                    all_keywords,
                    max_posts_per_subreddit
                )

                collected_posts.extend(subreddit_posts)
                posts_collected += len(subreddit_posts)

                self.logger.info(f"Collected {len(subreddit_posts)} posts from r/{subreddit_name}")

                # Rate limiting - be respectful to Reddit
                time.sleep(1)

            except Exception as e:
                self.logger.log_error_with_context(
                    e,
                    f"collecting from r/{subreddit_name}",
                    crisis_id=crisis_id
                )
                continue

        # Convert to DataFrame
        df = pd.DataFrame(collected_posts)

        end_time = datetime.now()
        self.logger.log_data_collection(
            platform='reddit',
            crisis_id=crisis_id,
            posts_collected=len(df),
            start_time=start_time,
            end_time=end_time,
            subreddits_searched=len(subreddits)
        )

        # Save raw data
        self._save_raw_data(df, crisis_id)

        return df

    def _search_subreddit_for_crisis(self,
                                   subreddit,
                                   keywords: List[str],
                                   max_posts: int) -> List[Dict]:
        """
        Search a subreddit for crisis-related posts

        Args:
            subreddit: Reddit subreddit object
            keywords (List[str]): Keywords to search for
            max_posts (int): Maximum posts to collect

        Returns:
            List[Dict]: List of post data dictionaries
        """
        posts = []

        try:
            # Search hot posts first
            hot_posts = list(subreddit.hot(limit=max_posts // 2))
            posts.extend(self._process_posts(hot_posts, keywords, subreddit.display_name))

            # Search recent posts
            if len(posts) < max_posts:
                recent_posts = list(subreddit.new(limit=max_posts // 2))
                posts.extend(self._process_posts(recent_posts, keywords, subreddit.display_name))

            # Search using keywords if we need more posts
            if len(posts) < max_posts and keywords:
                for keyword in keywords[:3]:  # Limit keyword searches
                    search_results = list(subreddit.search(
                        keyword,
                        time_filter='month',
                        limit=20
                    ))
                    posts.extend(self._process_posts(search_results, [keyword], subreddit.display_name))

                    if len(posts) >= max_posts:
                        break

        except Exception as e:
            self.logger.error(f"Error searching subreddit {subreddit.display_name}: {e}")

        return posts[:max_posts]  # Limit to max_posts

    def _process_posts(self,
                      posts_list,
                      keywords: List[str],
                      subreddit_name: str) -> List[Dict]:
        """
        Process Reddit posts and extract relevant information

        Args:
            posts_list: List of Reddit post objects
            keywords (List[str]): Keywords to filter by
            subreddit_name (str): Name of the subreddit

        Returns:
            List[Dict]: Processed post data
        """
        processed_posts = []

        for post in posts_list:
            try:
                # Check if post is crisis-relevant
                if not self._is_crisis_relevant(post, keywords):
                    continue

                # Extract post data
                post_data = {
                    'post_id': post.id,
                    'title': post.title,
                    'selftext': post.selftext if hasattr(post, 'selftext') else '',
                    'author': str(post.author) if post.author else '[deleted]',
                    'score': post.score,
                    'upvote_ratio': getattr(post, 'upvote_ratio', None),
                    'num_comments': post.num_comments,
                    'created_utc': datetime.fromtimestamp(post.created_utc),
                    'subreddit': subreddit_name,
                    'url': post.url if hasattr(post, 'url') else '',
                    'permalink': f"https://reddit.com{post.permalink}",
                    'is_self': getattr(post, 'is_self', False),
                    'platform': 'reddit',
                    'collected_at': datetime.now()
                }

                # Collect top comments
                post_data['comments'] = self._collect_top_comments(post, limit=5)

                processed_posts.append(post_data)

            except Exception as e:
                self.logger.error(f"Error processing post {getattr(post, 'id', 'unknown')}: {e}")
                continue

        return processed_posts

    def _is_crisis_relevant(self, post, keywords: List[str]) -> bool:
        """
        Check if a post is relevant to the crisis based on keywords

        Args:
            post: Reddit post object
            keywords (List[str]): Keywords to check for

        Returns:
            bool: True if post is crisis-relevant
        """
        # Combine title and text for keyword matching
        text_content = f"{post.title} {getattr(post, 'selftext', '')}"
        text_lower = text_content.lower()

        # Check for keyword matches
        for keyword in keywords:
            keyword_clean = keyword.replace('#', '').lower()
            if keyword_clean in text_lower:
                return True

        return False

    def _collect_top_comments(self, post, limit: int = 5) -> List[Dict]:
        """
        Collect top comments from a post

        Args:
            post: Reddit post object
            limit (int): Maximum number of comments to collect

        Returns:
            List[Dict]: Comment data
        """
        comments = []

        try:
            # Expand comment forest
            post.comments.replace_more(limit=0)

            for comment in post.comments[:limit]:
                try:
                    if hasattr(comment, 'body') and comment.body != '[deleted]':
                        comment_data = {
                            'comment_id': comment.id,
                            'body': comment.body,
                            'author': str(comment.author) if comment.author else '[deleted]',
                            'score': comment.score,
                            'created_utc': datetime.fromtimestamp(comment.created_utc),
                            'parent_id': comment.parent_id
                        }
                        comments.append(comment_data)
                except Exception as e:
                    continue

        except Exception as e:
            self.logger.error(f"Error collecting comments: {e}")

        return comments

    def _save_raw_data(self, df: pd.DataFrame, crisis_id: str):
        """
        Save raw data to files

        Args:
            df (pd.DataFrame): Data to save
            crisis_id (str): Crisis identifier
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save as CSV
        csv_path = self.raw_data_dir / f"{crisis_id}_reddit_sample_{timestamp}.csv"
        df.to_csv(csv_path, index=False)

        # Save as JSON for full data preservation
        json_path = self.raw_data_dir / f"{crisis_id}_reddit_sample_{timestamp}.json"
        df.to_json(json_path, orient='records', date_format='iso', indent=2)

        self.logger.info(f"Raw data saved: {csv_path} and {json_path}")

    def collect_all_crisis_samples(self, posts_per_crisis: int = 1500) -> Dict[str, pd.DataFrame]:
        """
        Collect sample data for all crisis events (Week 1 deliverable)

        Args:
            posts_per_crisis (int): Target posts per crisis event

        Returns:
            Dict[str, pd.DataFrame]: Data for each crisis
        """
        crisis_data = {}
        crisis_events = self.config.load_crisis_events()['crisis_events']

        self.logger.info(f"Collecting data for {len(crisis_events)} crisis events")

        for crisis_id in crisis_events.keys():
            self.logger.info(f"Starting collection for {crisis_id}")

            try:
                crisis_df = self.collect_crisis_sample_data(
                    crisis_id,
                    target_posts=posts_per_crisis
                )
                crisis_data[crisis_id] = crisis_df

                self.logger.info(f"Collected {len(crisis_df)} posts for {crisis_id}")

            except Exception as e:
                self.logger.log_error_with_context(
                    e,
                    f"collecting data for {crisis_id}",
                    crisis_id=crisis_id
                )
                crisis_data[crisis_id] = pd.DataFrame()  # Empty DataFrame on failure

        # Log summary
        total_posts = sum(len(df) for df in crisis_data.values())
        self.logger.info(f"Total posts collected across all crises: {total_posts}")

        return crisis_data

def run_initial_data_collection():
    """
    Run initial data collection for Week 1 deliverable
    Target: 2k-5k posts total across all crisis events
    """
    collector = RedditCrisisCollector()

    print("🚀 Starting Week 1 Initial Data Collection")
    print("Target: 2k-5k posts across all crisis events")

    # Collect data for all crises
    all_crisis_data = collector.collect_all_crisis_samples(posts_per_crisis=1500)

    # Print summary
    print("\n📊 Data Collection Summary:")
    print("=" * 50)

    total_posts = 0
    for crisis_id, df in all_crisis_data.items():
        posts_count = len(df)
        total_posts += posts_count
        print(f"{crisis_id}: {posts_count} posts")

    print(f"\nTotal posts collected: {total_posts}")

    if 2000 <= total_posts <= 10000:
        print("✅ Week 1 deliverable completed successfully!")
        print(f"✅ Target range (2k-5k) {'met' if total_posts <= 5000 else 'exceeded'}")
    else:
        print(f"⚠️  Collection outside target range. Adjust parameters if needed.")

    print(f"\n📁 Data saved in: data/raw/")
    print("🎯 Ready to proceed to Week 2!")

    return all_crisis_data

if __name__ == "__main__":
    run_initial_data_collection()
