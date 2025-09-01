import os
import praw
import pandas as pd
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import time

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
