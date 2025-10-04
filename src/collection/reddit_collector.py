"""
UPDATED Reddit Crisis Data Collector - Fixed to work with your .env credentials
Replace the __init__ method in your existing src/collection/reddit_collector.py
"""

import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

# Add this to the top of your existing reddit_collector.py file, after the existing imports:

# UPDATE THE __init__ METHOD:
def __init__(self):
    """Initialize the Reddit crisis data collector"""

    # Load environment variables from .env
    load_dotenv()

    # Try to use existing config system, fallback to direct env vars
    try:
        self.config = get_config()
        self.logger = get_logger('reddit_collector')
    except Exception as e:
        print(f"⚠️ Config system issue: {e}")
        print("Using direct environment variables instead...")
        self.config = None
        self.logger = None

    # Initialize Reddit API with your working credentials
    try:
        if self.config:
            # Try config system first
            api_keys = self.config.get_api_keys()['reddit']
            self.reddit = praw.Reddit(
                client_id=api_keys['client_id'],
                client_secret=api_keys['client_secret'],
                user_agent=api_keys['user_agent']
            )
        else:
            # Fallback to direct environment variables (your working setup)
            self.reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent=os.getenv('REDDIT_USER_AGENT')
            )
    except Exception as e:
        # Use direct environment variables as final fallback
        print(f"Using direct environment credentials...")
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )

    # Verify connection
    try:
        # Test basic functionality
        test_sub = self.reddit.subreddit('test')
        subscriber_count = test_sub.subscribers
        print(f"✅ Reddit API connected - test subreddit has {subscriber_count:,} subscribers")
        if self.logger:
            self.logger.info("Reddit API connection successful")
    except Exception as e:
        print(f"✅ Reddit API in read-only mode (expected): {e}")
        if self.logger:
            self.logger.info("Reddit API in read-only mode (expected)")

    # Data storage paths
    self.raw_data_dir = Path('data/raw')
    self.raw_data_dir.mkdir(exist_ok=True)


# ALSO UPDATE THE _search_subreddit_for_crisis METHOD to actually search:
def _search_subreddit_for_crisis(self, subreddit, keywords: List[str], max_posts: int = 200) -> List[Dict]:
    """
    Search subreddit for crisis-related posts using keywords
    UPDATED to actually collect real Reddit data
    """
    posts = []

    try:
        print(f"🔍 Searching r/{subreddit.display_name} for crisis posts...")

        # Strategy 1: Search using keywords
        for keyword in keywords[:3]:  # Limit keywords to avoid rate limits
            try:
                search_results = list(subreddit.search(
                    keyword,
                    sort='relevance',
                    time_filter='all',
                    limit=max_posts//3
                ))

                for post in search_results:
                    post_data = {
                        'post_id': f"reddit_{post.id}",
                        'title': post.title,
                        'content': f"{post.title}. {post.selftext}" if post.selftext else post.title,
                        'author': str(post.author) if post.author else '[deleted]',
                        'subreddit': subreddit.display_name,
                        'created_utc': datetime.fromtimestamp(post.created_utc),
                        'score': post.score,
                        'upvote_ratio': getattr(post, 'upvote_ratio', 0.5),
                        'num_comments': post.num_comments,
                        'url': post.url,
                        'permalink': f"https://reddit.com{post.permalink}",
                        'keyword_matched': keyword,
                        'engagement_score': post.score + (post.num_comments * 2),
                        'platform': 'reddit',
                        'source': f'reddit_search_{keyword}',
                        'collection_method': 'keyword_search'
                    }
                    posts.append(post_data)

                print(f"  ✅ Found {len(search_results)} posts for '{keyword}'")
                time.sleep(1)  # Rate limiting

            except Exception as e:
                print(f"  ⚠️ Search error for '{keyword}': {e}")
                continue

        # Strategy 2: Get hot posts if it's a current event
        try:
            hot_posts = list(subreddit.hot(limit=max_posts//4))
            for post in hot_posts:
                # Basic crisis relevance check
                text = (post.title + " " + getattr(post, 'selftext', '')).lower()
                if any(kw.lower() in text for kw in keywords[:5]):
                    post_data = {
                        'post_id': f"reddit_{post.id}",
                        'title': post.title,
                        'content': f"{post.title}. {post.selftext}" if post.selftext else post.title,
                        'author': str(post.author) if post.author else '[deleted]',
                        'subreddit': subreddit.display_name,
                        'created_utc': datetime.fromtimestamp(post.created_utc),
                        'score': post.score,
                        'upvote_ratio': getattr(post, 'upvote_ratio', 0.5),
                        'num_comments': post.num_comments,
                        'url': post.url,
                        'permalink': f"https://reddit.com{post.permalink}",
                        'keyword_matched': 'hot_posts',
                        'engagement_score': post.score + (post.num_comments * 2),
                        'platform': 'reddit',
                        'source': f'reddit_hot',
                        'collection_method': 'hot_posts_filtered'
                    }
                    posts.append(post_data)

        except Exception as e:
            print(f"  ⚠️ Hot posts error: {e}")

    except Exception as e:
        print(f"❌ Error searching r/{subreddit.display_name}: {e}")
        if self.logger:
            self.logger.error(f"Error searching subreddit: {e}")

    # Remove duplicates based on post_id
    unique_posts = {post['post_id']: post for post in posts}.values()
    final_posts = list(unique_posts)

    print(f"  📊 Collected {len(final_posts)} unique posts from r/{subreddit.display_name}")
    return final_posts
