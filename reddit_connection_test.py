#!/usr/bin/env python3
"""
Reddit API Connection Test
Tests the Reddit API credentials and basic functionality
"""
import os
import praw
from dotenv import load_dotenv
import sys
from pathlib import Path

def test_reddit_connection():
    """Test Reddit API connection with your credentials"""
    
    # Load environment variables
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ .env file not found!")
        print("Create .env file with your Reddit credentials:")
        print("REDDIT_CLIENT_ID=b4-VW3HaG7zH3cMxhU4Fkw")
        print("REDDIT_CLIENT_SECRET=Axpii9iW6qu9rnf39pE3Mg17gK5Ugg")
        print("REDDIT_USER_AGENT=Crisis Network Analysis Research by /u/yourusername")
        return False
    
    load_dotenv()
    
    # Get credentials from environment
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT')
    
    # Verify credentials are loaded
    if not all([client_id, client_secret, user_agent]):
        print("❌ Missing Reddit credentials in .env file!")
        print(f"CLIENT_ID: {'✅' if client_id else '❌'}")
        print(f"CLIENT_SECRET: {'✅' if client_secret else '❌'}")
        print(f"USER_AGENT: {'✅' if user_agent else '❌'}")
        return False
    
    try:
        # Initialize Reddit instance
        print("🔄 Testing Reddit API connection...")
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        # Test basic functionality
        print(f"✅ Reddit API initialized successfully!")
        print(f"✅ User Agent: {reddit.config.user_agent}")
        print(f"✅ Read-only mode: {reddit.read_only}")
        
        # Test subreddit access
        print("\n🔄 Testing subreddit access...")
        test_subreddit = reddit.subreddit('test')
        print(f"✅ Subreddit access: r/{test_subreddit.display_name}")
        print(f"✅ Subscribers: {test_subreddit.subscribers:,}")
        
        # Test crisis-relevant subreddits
        print("\n🔄 Testing crisis-relevant subreddits...")
        crisis_subreddits = ['LosAngeles', 'California', 'worldnews']
        
        for sub_name in crisis_subreddits:
            try:
                subreddit = reddit.subreddit(sub_name)
                print(f"✅ r/{subreddit.display_name}: {subreddit.subscribers:,} subscribers")
            except Exception as e:
                print(f"⚠️ r/{sub_name}: {str(e)}")
        
        # Test post collection (limited)
        print("\n🔄 Testing post collection...")
        try:
            test_posts = list(reddit.subreddit('test').hot(limit=3))
            print(f"✅ Successfully retrieved {len(test_posts)} test posts")
            
            for i, post in enumerate(test_posts, 1):
                print(f"  {i}. {post.title[:50]}...")
                
        except Exception as e:
            print(f"⚠️ Post collection test: {str(e)}")
        
        print("\n🎉 Reddit API connection test completed successfully!")
        print("🚀 Ready to collect crisis data!")
        return True
        
    except Exception as e:
        print(f"❌ Reddit API connection failed: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Verify your credentials in .env file")
        print("2. Check your Reddit app configuration at https://www.reddit.com/prefs/apps")
        print("3. Ensure your app is set as 'script' type")
        print("4. Wait a few minutes and try again")
        return False

def test_crisis_subreddits():
    """Test access to crisis-specific subreddits"""
    load_dotenv()
    
    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT')
    )
    
    # Crisis-specific subreddits from your project
    crisis_subreddits = {
        'LA Wildfires': ['LosAngeles', 'California', 'wildfire', 'CaliforniaWildfires'],
        'India-Pakistan': ['india', 'pakistan', 'Kashmir', 'worldnews', 'geopolitics'],
        'Turkey-Syria': ['Turkey', 'syria', 'earthquake', 'worldnews']
    }
    
    print("🔥 Testing Crisis-Specific Subreddits")
    print("=" * 50)
    
    for crisis, subreddits in crisis_subreddits.items():
        print(f"\n📊 {crisis} Crisis Subreddits:")
        for sub_name in subreddits:
            try:
                subreddit = reddit.subreddit(sub_name)
                print(f"✅ r/{subreddit.display_name}: {subreddit.subscribers:,} subscribers")
            except Exception as e:
                print(f"❌ r/{sub_name}: {str(e)}")

if __name__ == "__main__":
    print("🔍 Reddit API Connection Test for Crisis Network Analysis")
    print("=" * 60)
    
    # Test basic connection
    if test_reddit_connection():
        print("\n" + "=" * 60)
        test_crisis_subreddits()
    else:
        print("\n❌ Basic connection failed. Fix credentials before testing subreddits.")
        sys.exit(1)
