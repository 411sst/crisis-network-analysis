"""
Expanded Reddit Crisis Data Collector - Option A Implementation
Adds more subreddits, time filters, and collection strategies to get fresh data
"""

import os
import praw
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import time
import json
from pathlib import Path
from dotenv import load_dotenv
import hashlib

class ExpandedRedditCrisisCollector:
    """Expanded Reddit collector with broader scope"""
    
    def __init__(self):
        load_dotenv()
        
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        
        # Expanded crisis configurations with many more subreddits
        self.expanded_configs = {
            'la_wildfires_2025': {
                'name': 'Los Angeles Wildfires 2025',
                'subreddits': {
                    'primary': ['LosAngeles', 'California', 'wildfire'],
                    'secondary': ['CaliforniaWildfires', 'Malibu', 'Pasadena', 'SantaMonica'],
                    'emergency': ['emergency', 'news', 'NaturalDisasters'],
                    'local': ['burbank', 'glendale', 'beverlyhills', 'calabasas'],
                    'general': ['pics', 'videos', 'climate']
                },
                'keywords': {
                    'fire_specific': [
                        'palisades fire', 'eaton fire', 'woolsey fire', 'thomas fire',
                        'camp fire', 'rim fire', 'creek fire'
                    ],
                    'location_specific': [
                        'malibu fire', 'altadena fire', 'pacific palisades fire',
                        'topanga fire', 'santa monica mountains fire'
                    ],
                    'emergency_terms': [
                        'red flag warning', 'fire weather', 'santa ana winds',
                        'evacuation zone', 'mandatory evacuation', 'fire department'
                    ],
                    'general_fire': [
                        'california wildfire', 'southern california fire', 'la fire',
                        'fire season', 'drought fire', 'brush fire'
                    ]
                },
                'time_strategies': ['day', 'week', 'month', 'year', 'all']
            },
            'india_pakistan_2025': {
                'name': 'India-Pakistan Conflict 2025',
                'subreddits': {
                    'primary': ['india', 'pakistan', 'worldnews'],
                    'secondary': ['Kashmir', 'geopolitics', 'IndiaNews'],
                    'regional': ['indianews', 'chutyapa', 'bakchodi'],
                    'international': ['news', 'internationalpolitics', 'worldpolitics'],
                    'analysis': ['geopolitics', 'NeutralPolitics', 'CredibleDefense']
                },
                'keywords': {
                    'conflict_terms': [
                        'india pakistan border', 'line of control', 'loc tension',
                        'cross border firing', 'ceasefire violation'
                    ],
                    'military_terms': [
                        'surgical strike', 'air strike', 'military operation',
                        'army chief', 'defense minister'
                    ],
                    'diplomatic_terms': [
                        'diplomatic crisis', 'peace talks', 'foreign minister',
                        'embassy relations', 'trade suspension'
                    ],
                    'regional_terms': [
                        'kashmir issue', 'azad kashmir', 'jammu kashmir',
                        'siachen glacier', 'kargil'
                    ]
                },
                'time_strategies': ['week', 'month', 'year', 'all']
            },
            'turkey_syria_earthquake_2023': {
                'name': 'Turkey-Syria Earthquake 2023',
                'subreddits': {
                    'primary': ['Turkey', 'syria', 'worldnews'],
                    'secondary': ['earthquake', 'syriancivilwar'],
                    'disaster': ['NaturalDisasters', 'geology', 'science'],
                    'humanitarian': ['HumansBeingBros', 'MadeMeSmile', 'UpliftingNews'],
                    'news': ['news', 'europe', 'MiddleEastNews']
                },
                'keywords': {
                    'earthquake_terms': [
                        'turkey earthquake', 'syria earthquake', 'kahramanmaras',
                        'gaziantep earthquake', 'hatay earthquake', 'adana earthquake'
                    ],
                    'disaster_response': [
                        'search and rescue', 'emergency response', 'disaster relief',
                        'humanitarian aid', 'rescue teams', 'survivors'
                    ],
                    'international_aid': [
                        'international aid', 'red cross', 'un assistance',
                        'aid organizations', 'emergency funds', 'donations'
                    ],
                    'technical_terms': [
                        'richter scale', 'aftershock', 'seismic activity',
                        'fault line', 'tectonic plates', 'magnitude'
                    ]
                },
                'time_strategies': ['month', 'year', 'all']
            }
        }
        
        self.raw_data_dir = Path('data/raw')
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Expanded Reddit Collector initialized with {sum(len(c['subreddits']) for c in self.expanded_configs.values())} total subreddits")
    
    def collect_expanded_crisis_data(self, crisis_id: str, target_posts: int = 2000) -> pd.DataFrame:
        """Collect data using expanded scope and strategies"""
        if crisis_id not in self.expanded_configs:
            raise ValueError(f"Unknown crisis ID: {crisis_id}")
        
        config = self.expanded_configs[crisis_id]
        print(f"Starting expanded collection for {config['name']}")
        print(f"Target: {target_posts} posts")
        
        all_posts = []
        
        # Strategy 1: Search all subreddit categories with different time filters
        for category, subreddits in config['subreddits'].items():
            print(f"Collecting from {category} subreddits: {subreddits}")
            
            for subreddit_name in subreddits:
                # Use different time filters for variety
                for time_filter in ['week', 'month', 'all']:
                    posts = self._search_expanded_subreddit(
                        subreddit_name, config['keywords'], time_filter, 
                        target_posts // (len(config['subreddits']) * 2)
                    )
                    all_posts.extend(posts)
                    
                    if len(all_posts) >= target_posts:
                        break
                        
                if len(all_posts) >= target_posts:
                    break
                    
            if len(all_posts) >= target_posts:
                break
        
        # Strategy 2: Sort-based collection (hot, new, top) from primary subreddits
        if len(all_posts) < target_posts:
            remaining_target = target_posts - len(all_posts)
            sort_posts = self._collect_by_sorting(crisis_id, remaining_target // 3)
            all_posts.extend(sort_posts)
        
        # Process collected data
        df = self._process_expanded_data(all_posts, crisis_id, target_posts)
        
        # Save expanded data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{crisis_id}_expanded_{timestamp}.csv"
        filepath = self.raw_data_dir / filename
        df.to_csv(filepath, index=False)
        
        print(f"Expanded collection completed: {len(df)} posts")
        print(f"Saved to: {filepath}")
        
        return df
    
    def _search_expanded_subreddit(self, subreddit_name: str, keywords: Dict[str, List[str]], 
                                 time_filter: str, limit: int) -> List[Dict]:
        """Search subreddit with expanded keyword categories"""
        posts = []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Search each keyword category
            for category, keyword_list in keywords.items():
                for keyword in keyword_list[:2]:  # Limit to prevent rate limiting
                    try:
                        search_results = list(subreddit.search(
                            keyword,
                            sort='relevance',
                            time_filter=time_filter,
                            limit=min(20, limit // 4)
                        ))
                        
                        for post in search_results:
                            post_data = self._extract_expanded_post_data(
                                post, subreddit_name, keyword, f"search_{time_filter}"
                            )
                            if post_data:
                                posts.append(post_data)
                        
                        time.sleep(0.5)  # Reduced delay for faster collection
                        
                    except Exception as e:
                        print(f"  Search error for '{keyword}': {e}")
                        continue
                        
            print(f"  Collected {len(posts)} posts from r/{subreddit_name} ({time_filter})")
            
        except Exception as e:
            print(f"  Error accessing r/{subreddit_name}: {e}")
            
        return posts
    
    def _collect_by_sorting(self, crisis_id: str, target_posts: int) -> List[Dict]:
        """Collect using different sorting methods"""
        config = self.expanded_configs[crisis_id]
        posts = []
        
        primary_subreddits = config['subreddits']['primary']
        
        for subreddit_name in primary_subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Get hot posts
                hot_posts = list(subreddit.hot(limit=target_posts // 6))
                for post in hot_posts:
                    if self._is_crisis_relevant_expanded(post, config):
                        post_data = self._extract_expanded_post_data(
                            post, subreddit_name, 'sort_filter', 'hot_posts'
                        )
                        if post_data:
                            posts.append(post_data)
                
                # Get top posts (weekly)
                top_posts = list(subreddit.top(time_filter='week', limit=target_posts // 6))
                for post in top_posts:
                    if self._is_crisis_relevant_expanded(post, config):
                        post_data = self._extract_expanded_post_data(
                            post, subreddit_name, 'sort_filter', 'top_weekly'
                        )
                        if post_data:
                            posts.append(post_data)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"  Sort collection error for r/{subreddit_name}: {e}")
        
        print(f"  Sort-based collection: {len(posts)} posts")
        return posts
    
    def _is_crisis_relevant_expanded(self, post, config: Dict) -> bool:
        """Expanded crisis relevance check"""
        text = (post.title + " " + getattr(post, 'selftext', '')).lower()
        
        # Check against all keyword categories
        for keyword_category in config['keywords'].values():
            for keyword in keyword_category:
                if keyword.lower() in text:
                    return True
        
        return False
    
    def _extract_expanded_post_data(self, post, subreddit_name: str, keyword: str, 
                                  collection_method: str) -> Optional[Dict]:
        """Extract post data with expanded metadata"""
        try:
            return {
                'post_id': f"reddit_{post.id}",
                'title': post.title,
                'content': f"{post.title}. {post.selftext}" if post.selftext else post.title,
                'author': str(post.author) if post.author else '[deleted]',
                'subreddit': subreddit_name,
                'created_utc': datetime.fromtimestamp(post.created_utc),
                'score': post.score,
                'upvote_ratio': getattr(post, 'upvote_ratio', 0.5),
                'num_comments': post.num_comments,
                'url': post.url,
                'permalink': f"https://reddit.com{post.permalink}",
                'keyword_matched': keyword,
                'collection_method': collection_method,
                'platform': 'reddit',
                'engagement_score': post.score + (post.num_comments * 2),
                'content_hash': hashlib.md5(f"{post.title}{post.selftext}".encode()).hexdigest()[:12],
                'collection_timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"  Error extracting post: {e}")
            return None
    
    def _process_expanded_data(self, posts: List[Dict], crisis_id: str, target_posts: int) -> pd.DataFrame:
        """Process expanded data collection"""
        if not posts:
            return pd.DataFrame()
        
        df = pd.DataFrame(posts)
        
        # Remove duplicates
        initial_count = len(df)
        df = df.drop_duplicates(subset=['content_hash'])
        print(f"  Removed {initial_count - len(df)} duplicate posts")
        
        # Add crisis metadata
        df['crisis_id'] = crisis_id
        df['crisis_name'] = self.expanded_configs[crisis_id]['name']
        
        # Sort by engagement
        df = df.sort_values('engagement_score', ascending=False)
        
        # Limit to target
        if len(df) > target_posts:
            df = df.head(target_posts)
        
        return df

def run_expanded_collection():
    """Run expanded collection for all crises"""
    collector = ExpandedRedditCrisisCollector()
    
    print("EXPANDED REDDIT CRISIS DATA COLLECTION")
    print("=" * 60)
    
    # Higher targets for expanded collection
    expanded_targets = {
        'la_wildfires_2025': 1000,
        'turkey_syria_earthquake_2023': 600, 
        'india_pakistan_2025': 500
    }
    
    all_data = {}
    
    for crisis_id, target in expanded_targets.items():
        try:
            crisis_df = collector.collect_expanded_crisis_data(crisis_id, target)
            all_data[crisis_id] = crisis_df
        except Exception as e:
            print(f"Error collecting {crisis_id}: {e}")
            all_data[crisis_id] = pd.DataFrame()
    
    # Combine all expanded data
    total_posts = sum(len(df) for df in all_data.values())
    
    if total_posts > 0:
        combined_df = pd.concat([df for df in all_data.values() if not df.empty], 
                               ignore_index=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        combined_path = collector.raw_data_dir / f"all_crises_expanded_{timestamp}.csv"
        combined_df.to_csv(combined_path, index=False)
        
        print(f"\nEXPANDED COLLECTION SUMMARY:")
        print(f"Total expanded posts: {total_posts}")
        print(f"Combined dataset: {combined_path}")
        
        for crisis_id, df in all_data.items():
            config = collector.expanded_configs[crisis_id]
            print(f"  {config['name']}: {len(df)} posts")
    
    return all_data

if __name__ == "__main__":
    run_expanded_collection()
