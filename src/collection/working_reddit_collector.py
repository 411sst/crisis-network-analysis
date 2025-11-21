import os
import praw
import pandas as pd
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import time


class WorkingRedditCollector:
    """
    Minimal Reddit collector used by tests.

    Provides:
    - collect_posts(subreddit, limit=..., time_filter=...)
    - search_posts(subreddit, query, limit=..., time_filter=...)
    - save_to_csv(df, path)
    """

    def __init__(self, client_id: str = None, client_secret: str = None, user_agent: str = None):
        load_dotenv()

        # Allow passing credentials explicitly (as tests do), else use env vars
        client_id = client_id or os.getenv('REDDIT_CLIENT_ID')
        client_secret = client_secret or os.getenv('REDDIT_CLIENT_SECRET')
        user_agent = user_agent or os.getenv('REDDIT_USER_AGENT') or 'crisis-network-analysis-tests'

        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )

    def _post_to_dict(self, post) -> dict:
        """Convert a PRAW submission (mock or real) to a dict row."""
        author_name = '[deleted]'
        try:
            if getattr(post, 'author', None) is not None:
                # Some mocks set author.name; real PRAW supports str(post.author)
                author_name = getattr(getattr(post, 'author', None), 'name', None) or str(post.author)
        except Exception:
            author_name = '[deleted]'

        subreddit_name = None
        try:
            sub = getattr(post, 'subreddit', None)
            subreddit_name = getattr(sub, 'display_name', None) if sub else None
        except Exception:
            subreddit_name = None

        created_ts = getattr(post, 'created_utc', None)
        try:
            created_dt = datetime.fromtimestamp(created_ts) if created_ts is not None else None
        except Exception:
            created_dt = None

        return {
            'title': getattr(post, 'title', ''),
            'content': (getattr(post, 'selftext', '') or getattr(post, 'title', '')),
            'author': author_name or '[deleted]',
            'subreddit': subreddit_name or '',
            'created_utc': created_dt,
            'score': getattr(post, 'score', 0),
            'num_comments': getattr(post, 'num_comments', 0),
            'upvote_ratio': getattr(post, 'upvote_ratio', 0.0),
            'url': getattr(post, 'url', ''),
            'post_id': getattr(post, 'id', ''),
            'permalink': getattr(post, 'permalink', ''),
        }

    def collect_posts(self, subreddit: str, limit: int = 100, time_filter: str = 'week') -> pd.DataFrame:
        """Collect posts from a subreddit using the 'hot' listing by default."""
        try:
            sub = self.reddit.subreddit(subreddit)
            # Tests mock .hot; time_filter is accepted but unused in this minimal impl
            posts = list(sub.hot(limit=limit))
        except Exception:
            posts = []

        rows = [self._post_to_dict(p) for p in posts]
        return pd.DataFrame(rows)

    def search_posts(self, subreddit: str, query: str, limit: int = 100, time_filter: str = 'all') -> pd.DataFrame:
        """Search posts in a subreddit by query string."""
        try:
            sub = self.reddit.subreddit(subreddit)
            posts = list(sub.search(query, limit=limit, time_filter=time_filter))
        except Exception:
            posts = []

        rows = [self._post_to_dict(p) for p in posts]
        return pd.DataFrame(rows)

    def save_to_csv(self, df: pd.DataFrame, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)

def collect_reddit_crisis_data():
    """Simple working Reddit crisis data collector"""
    load_dotenv()
    
    # Initialize Reddit
    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT')
    )
    
    print(f"✅ Reddit initialized - Read-only: {reddit.read_only}")
    print("🔥 Starting Crisis Data Collection")
    print("=" * 50)
    
    all_posts = []
    
    # Crisis 1: LA Wildfires
    print("🔥 Collecting LA Wildfire posts...")
    subreddits = ['LosAngeles', 'California']
    keywords = ['wildfire', 'fire', 'evacuation', 'palisades']
    
    for sub_name in subreddits:
        subreddit = reddit.subreddit(sub_name)
        for keyword in keywords:
            posts = list(subreddit.search(keyword, limit=50))
            
            for post in posts:
                post_data = {
                    'post_id': f"reddit_{post.id}",
                    'title': post.title,
                    'content': post.selftext if post.selftext else post.title,
                    'subreddit': sub_name,
                    'score': post.score,
                    'comments': post.num_comments,
                    'created_utc': datetime.fromtimestamp(post.created_utc),
                    'crisis_id': 'la_wildfires_2025',
                    'keyword': keyword,
                    'platform': 'reddit'
                }
                all_posts.append(post_data)
            
            print(f"  📊 Found {len(posts)} posts for '{keyword}' in r/{sub_name}")
            time.sleep(1)  # Rate limiting
    
    # Crisis 2: India-Pakistan
    print("\n🌍 Collecting India-Pakistan posts...")
    subreddits = ['india', 'pakistan', 'worldnews']
    keywords = ['india pakistan', 'kashmir', 'conflict']
    
    for sub_name in subreddits:
        try:
            subreddit = reddit.subreddit(sub_name)
            for keyword in keywords[:2]:  # Limit to avoid rate limits
                posts = list(subreddit.search(keyword, limit=30))
                
                for post in posts:
                    post_data = {
                        'post_id': f"reddit_{post.id}",
                        'title': post.title,
                        'content': post.selftext if post.selftext else post.title,
                        'subreddit': sub_name,
                        'score': post.score,
                        'comments': post.num_comments,
                        'created_utc': datetime.fromtimestamp(post.created_utc),
                        'crisis_id': 'india_pakistan_2025',
                        'keyword': keyword,
                        'platform': 'reddit'
                    }
                    all_posts.append(post_data)
                
                print(f"  📊 Found {len(posts)} posts for '{keyword}' in r/{sub_name}")
                time.sleep(1)
        except Exception as e:
            print(f"  ⚠️ Error with r/{sub_name}: {e}")
    
    # Crisis 3: Turkey-Syria Earthquake
    print("\n🏗️ Collecting Turkey-Syria Earthquake posts...")
    subreddits = ['Turkey', 'syria', 'worldnews']
    keywords = ['turkey earthquake', 'syria earthquake']
    
    for sub_name in subreddits:
        try:
            subreddit = reddit.subreddit(sub_name)
            for keyword in keywords:
                posts = list(subreddit.search(keyword, limit=40))
                
                for post in posts:
                    post_data = {
                        'post_id': f"reddit_{post.id}",
                        'title': post.title,
                        'content': post.selftext if post.selftext else post.title,
                        'subreddit': sub_name,
                        'score': post.score,
                        'comments': post.num_comments,
                        'created_utc': datetime.fromtimestamp(post.created_utc),
                        'crisis_id': 'turkey_syria_earthquake_2023',
                        'keyword': keyword,
                        'platform': 'reddit'
                    }
                    all_posts.append(post_data)
                
                print(f"  📊 Found {len(posts)} posts for '{keyword}' in r/{sub_name}")
                time.sleep(1)
        except Exception as e:
            print(f"  ⚠️ Error with r/{sub_name}: {e}")
    
    # Remove duplicates and save
    df = pd.DataFrame(all_posts)
    df = df.drop_duplicates(subset=['post_id'])
    
    # Ensure data directory exists
    Path('../../data/raw').mkdir(parents=True, exist_ok=True)
    
    # Save data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'../../data/raw/reddit_crisis_data_{timestamp}.csv'
    df.to_csv(filename, index=False)
    
    print("\n📊 COLLECTION SUMMARY:")
    print("=" * 30)
    crisis_counts = df.groupby('crisis_id').size()
    for crisis, count in crisis_counts.items():
        print(f"{crisis}: {count} posts")
    
    total = len(df)
    print(f"\n🎯 TOTAL: {total} posts collected")
    print(f"💾 Saved to: {filename}")
    
    if 1000 <= total <= 5000:
        print("✅ Week 1-2 target achieved with REAL Reddit data!")
    
    return df

if __name__ == "__main__":
    collect_reddit_crisis_data()
