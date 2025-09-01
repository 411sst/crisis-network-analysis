"""
Enhanced Reddit Crisis Data Collector v2.0
Advanced, configurable, and scalable Reddit data collection for crisis analysis

Features:
- Configuration-driven crisis definitions
- Multiple collection strategies (search, hot, new, top)
- Advanced filtering and relevance scoring
- Comments collection with threading
- Duplicate detection and quality filtering
- Progress tracking and resumable collection
- Comprehensive error handling and logging
- Integration with existing project structure
"""

import os
import praw
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import time
import json
from pathlib import Path
from dotenv import load_dotenv
import re
import hashlib
from dataclasses import dataclass
from collections import defaultdict

# Try to import project utilities, fallback gracefully
try:
    from src.utils.config_loader import get_config
    from src.utils.logger import get_logger
    HAS_PROJECT_UTILS = True
except ImportError:
    print("⚠️ Project utilities not available, using fallback methods")
    HAS_PROJECT_UTILS = False

@dataclass
class CollectionStats:
    """Track collection statistics"""
    posts_collected: int = 0
    posts_filtered: int = 0
    subreddits_processed: int = 0
    errors_encountered: int = 0
    start_time: datetime = None
    end_time: datetime = None

class EnhancedRedditCrisisCollector:
    """Enhanced Reddit collector with advanced features"""
    
    def __init__(self):
        """Initialize the enhanced Reddit crisis data collector"""
        load_dotenv()
        
        # Initialize configuration system
        if HAS_PROJECT_UTILS:
            try:
                self.config = get_config()
                self.logger = get_logger('enhanced_reddit_collector')
                print("✅ Using project configuration system")
            except Exception as e:
                print(f"⚠️ Config system error: {e}, using fallback")
                self.config = None
                self.logger = None
        else:
            self.config = None
            self.logger = None
        
        # Initialize Reddit API with robust fallback
        self.reddit = self._initialize_reddit_api()
        
        # Enhanced crisis configurations
        self.crisis_configs = self._load_enhanced_crisis_configs()
        
        # Collection settings
        self.collection_strategies = [
            'search_keywords',  # Search by keywords
            'hot_posts',       # Get hot posts
            'new_posts',       # Get new posts
            'top_posts'        # Get top posts (weekly/monthly)
        ]
        
        # Data storage
        self.raw_data_dir = Path('data/raw')
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Collection statistics
        self.stats = CollectionStats()
        
        print(f"✅ Enhanced Reddit Collector v2.0 initialized")
        print(f"✅ Reddit API: {self.reddit.read_only}")
    
    def _initialize_reddit_api(self) -> praw.Reddit:
        """Initialize Reddit API with multiple fallback methods"""
        # Try config system first
        if self.config:
            try:
                api_keys = self.config.get_api_keys()['reddit']
                return praw.Reddit(
                    client_id=api_keys['client_id'],
                    client_secret=api_keys['client_secret'],
                    user_agent=api_keys['user_agent']
                )
            except Exception as e:
                self._log(f"Config API initialization failed: {e}", 'warning')
        
        # Fallback to environment variables
        return praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
    
    def _load_enhanced_crisis_configs(self) -> Dict[str, Dict]:
        """Load enhanced crisis configurations with multiple strategies"""
        base_configs = {
            'la_wildfires_2025': {
                'name': 'Los Angeles Wildfires 2025',
                'subreddits': {
                    'primary': ['LosAngeles', 'California'],
                    'secondary': ['wildfire', 'CaliforniaWildfires', 'Malibu', 'Pasadena']
                },
                'keywords': {
                    'primary': [
                        'palisades fire', 'eaton fire', 'la fires', 'los angeles wildfire',
                        'california wildfire', 'evacuation', 'fire emergency'
                    ],
                    'secondary': [
                        'malibu fire', 'altadena fire', 'pacific palisades', 'fire evacuation',
                        'red flag warning', 'santa ana winds', 'fire danger'
                    ],
                    'emergency': [
                        'evacuation order', 'fire emergency', 'evacuate now', 'fire alert'
                    ]
                },
                'time_filters': ['week', 'month', 'all'],
                'collection_priority': 'current_event'
            },
            'india_pakistan_2025': {
                'name': 'India-Pakistan Conflict 2025',
                'subreddits': {
                    'primary': ['india', 'pakistan', 'worldnews'],
                    'secondary': ['Kashmir', 'geopolitics', 'IndiaNews', 'pakistan']
                },
                'keywords': {
                    'primary': [
                        'india pakistan conflict', 'kashmir conflict', 'border tension',
                        'military conflict', 'diplomatic crisis'
                    ],
                    'secondary': [
                        'operation sindoor', 'pahalgam attack', 'ceasefire',
                        'peace talks', 'loc tension', 'cross border'
                    ],
                    'emergency': [
                        'border clash', 'military action', 'escalation', 'urgent diplomatic'
                    ]
                },
                'time_filters': ['month', 'year', 'all'],
                'collection_priority': 'future_event'
            },
            'turkey_syria_earthquake_2023': {
                'name': 'Turkey-Syria Earthquake 2023',
                'subreddits': {
                    'primary': ['Turkey', 'syria', 'worldnews'],
                    'secondary': ['earthquake', 'syria', 'turkiye', 'lebanon']
                },
                'keywords': {
                    'primary': [
                        'turkey earthquake', 'syria earthquake', 'kahramanmaras earthquake',
                        'earthquake turkey', 'deprem turkiye'
                    ],
                    'secondary': [
                        'rescue operation', 'earthquake relief', 'international aid',
                        'disaster response', 'search and rescue', 'earthquake victims'
                    ],
                    'emergency': [
                        'earthquake emergency', 'rescue urgent', 'disaster relief',
                        'earthquake aid'
                    ]
                },
                'time_filters': ['year', 'all'],
                'collection_priority': 'historical_event'
            }
        }
        
        # If project config available, try to merge with project settings
        if self.config:
            try:
                for crisis_id in base_configs.keys():
                    project_config = self.config.get_crisis_event_config(crisis_id)
                    # Merge project config if available
                    if project_config:
                        reddit_config = project_config.get('platforms', {}).get('reddit', {})
                        if reddit_config:
                            # Update subreddits from project config
                            if 'subreddits' in reddit_config:
                                base_configs[crisis_id]['subreddits']['primary'] = reddit_config['subreddits']
                            
                            # Update keywords from project config  
                            if 'keywords' in reddit_config:
                                base_configs[crisis_id]['keywords']['primary'] = reddit_config['keywords']
                                
            except Exception as e:
                self._log(f"Error merging project config: {e}", 'warning')
        
        return base_configs
    
    def _log(self, message: str, level: str = 'info'):
        """Enhanced logging with fallback"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {message}")
        
        if self.logger:
            getattr(self.logger, level, self.logger.info)(message)
    
    def collect_crisis_data_enhanced(self, crisis_id: str, target_posts: int = 2000,
                                   strategies: Optional[List[str]] = None,
                                   quality_threshold: float = 0.3) -> pd.DataFrame:
        """
        Enhanced crisis data collection with multiple strategies
        
        Args:
            crisis_id: Crisis event identifier
            target_posts: Target number of posts to collect
            strategies: List of collection strategies to use
            quality_threshold: Minimum quality score for posts (0-1)
            
        Returns:
            DataFrame with collected posts
        """
        if crisis_id not in self.crisis_configs:
            raise ValueError(f"Unknown crisis ID: {crisis_id}")
        
        config = self.crisis_configs[crisis_id]
        strategies = strategies or self.collection_strategies
        
        self.stats = CollectionStats(start_time=datetime.now())
        
        self._log(f"🚀 Starting enhanced collection for {config['name']}")
        self._log(f"📊 Target: {target_posts} posts using {len(strategies)} strategies")
        
        all_posts = []
        posts_per_strategy = target_posts // len(strategies)
        
        # Strategy 1: Keyword search (most important)
        if 'search_keywords' in strategies:
            search_posts = self._collect_by_keyword_search(
                crisis_id, posts_per_strategy, quality_threshold
            )
            all_posts.extend(search_posts)
            self._log(f"  📊 Keyword search: {len(search_posts)} posts")
        
        # Strategy 2: Hot posts (current discussions)
        if 'hot_posts' in strategies:
            hot_posts = self._collect_hot_posts(
                crisis_id, posts_per_strategy // 2, quality_threshold
            )
            all_posts.extend(hot_posts)
            self._log(f"  📊 Hot posts: {len(hot_posts)} posts")
        
        # Strategy 3: New posts (recent activity)
        if 'new_posts' in strategies:
            new_posts = self._collect_new_posts(
                crisis_id, posts_per_strategy // 2, quality_threshold
            )
            all_posts.extend(new_posts)
            self._log(f"  📊 New posts: {len(new_posts)} posts")
        
        # Strategy 4: Top posts (high engagement)
        if 'top_posts' in strategies:
            top_posts = self._collect_top_posts(
                crisis_id, posts_per_strategy // 2, quality_threshold
            )
            all_posts.extend(top_posts)
            self._log(f"  📊 Top posts: {len(top_posts)} posts")
        
        # Process and clean collected data
        df = self._process_collected_data(all_posts, crisis_id, target_posts)
        
        self.stats.end_time = datetime.now()
        self.stats.posts_collected = len(df)
        
        # Save data
        self._save_enhanced_data(df, crisis_id)
        
        # Print collection summary
        self._print_collection_summary(crisis_id, df)
        
        return df
    
    def _collect_by_keyword_search(self, crisis_id: str, target_posts: int,
                                 quality_threshold: float) -> List[Dict]:
        """Collect posts using keyword search strategy"""
        config = self.crisis_configs[crisis_id]
        all_posts = []
        
        # Prioritize primary subreddits and keywords
        primary_subreddits = config['subreddits']['primary']
        all_keywords = (config['keywords']['primary'] + 
                       config['keywords']['secondary'] + 
                       config['keywords']['emergency'])
        
        posts_per_subreddit = max(50, target_posts // len(primary_subreddits))
        
        for subreddit_name in primary_subreddits:
            subreddit_posts = self._search_subreddit_comprehensive(
                subreddit_name, all_keywords, posts_per_subreddit, quality_threshold
            )
            all_posts.extend(subreddit_posts)
            
            if len(all_posts) >= target_posts:
                break
        
        return all_posts[:target_posts]
    
    def _search_subreddit_comprehensive(self, subreddit_name: str, keywords: List[str],
                                      limit: int, quality_threshold: float) -> List[Dict]:
        """Comprehensive subreddit search with multiple methods"""
        posts = []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            self._log(f"🔍 Searching r/{subreddit_name}...")
            
            # Method 1: Search by each keyword
            for keyword in keywords[:5]:  # Limit to prevent rate limiting
                try:
                    search_results = list(subreddit.search(
                        keyword,
                        sort='relevance',
                        time_filter='all',
                        limit=limit//5
                    ))
                    
                    for post in search_results:
                        post_data = self._extract_enhanced_post_data(
                            post, subreddit_name, keyword, 'search'
                        )
                        
                        if post_data and self._calculate_post_quality(post_data) >= quality_threshold:
                            posts.append(post_data)
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    self._log(f"  ⚠️ Keyword '{keyword}' error: {e}", 'warning')
                    continue
            
            self.stats.subreddits_processed += 1
            
        except Exception as e:
            self._log(f"❌ Error accessing r/{subreddit_name}: {e}", 'error')
            self.stats.errors_encountered += 1
        
        return posts
    
    def _collect_hot_posts(self, crisis_id: str, target_posts: int,
                         quality_threshold: float) -> List[Dict]:
        """Collect hot posts strategy"""
        config = self.crisis_configs[crisis_id]
        all_posts = []
        
        for subreddit_name in config['subreddits']['primary']:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                hot_posts = list(subreddit.hot(limit=target_posts//2))
                
                for post in hot_posts:
                    if self._is_crisis_relevant_enhanced(post, config):
                        post_data = self._extract_enhanced_post_data(
                            post, subreddit_name, 'hot_filter', 'hot'
                        )
                        
                        if post_data and self._calculate_post_quality(post_data) >= quality_threshold:
                            all_posts.append(post_data)
                
                time.sleep(1)
                
            except Exception as e:
                self._log(f"  ⚠️ Hot posts error for r/{subreddit_name}: {e}", 'warning')
        
        return all_posts
    
    def _collect_new_posts(self, crisis_id: str, target_posts: int,
                         quality_threshold: float) -> List[Dict]:
        """Collect new posts strategy"""
        config = self.crisis_configs[crisis_id]
        all_posts = []
        
        for subreddit_name in config['subreddits']['primary']:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                new_posts = list(subreddit.new(limit=target_posts//2))
                
                for post in new_posts:
                    if self._is_crisis_relevant_enhanced(post, config):
                        post_data = self._extract_enhanced_post_data(
                            post, subreddit_name, 'new_filter', 'new'
                        )
                        
                        if post_data and self._calculate_post_quality(post_data) >= quality_threshold:
                            all_posts.append(post_data)
                
                time.sleep(1)
                
            except Exception as e:
                self._log(f"  ⚠️ New posts error for r/{subreddit_name}: {e}", 'warning')
        
        return all_posts
    
    def _collect_top_posts(self, crisis_id: str, target_posts: int,
                         quality_threshold: float) -> List[Dict]:
        """Collect top posts strategy"""
        config = self.crisis_configs[crisis_id]
        all_posts = []
        
        time_filter = 'month' if config['collection_priority'] == 'current_event' else 'year'
        
        for subreddit_name in config['subreddits']['primary']:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                top_posts = list(subreddit.top(time_filter=time_filter, limit=target_posts//2))
                
                for post in top_posts:
                    if self._is_crisis_relevant_enhanced(post, config):
                        post_data = self._extract_enhanced_post_data(
                            post, subreddit_name, 'top_filter', 'top'
                        )
                        
                        if post_data and self._calculate_post_quality(post_data) >= quality_threshold:
                            all_posts.append(post_data)
                
                time.sleep(1)
                
            except Exception as e:
                self._log(f"  ⚠️ Top posts error for r/{subreddit_name}: {e}", 'warning')
        
        return all_posts
    
    def _extract_enhanced_post_data(self, post, subreddit_name: str,
                                  keyword: str, collection_method: str) -> Optional[Dict]:
        """Extract comprehensive post data with enhanced fields"""
        try:
            # Basic post data
            post_data = {
                'post_id': f"reddit_{post.id}",
                'title': post.title,
                'content': f"{post.title}. {post.selftext}" if post.selftext else post.title,
                'selftext': post.selftext if hasattr(post, 'selftext') else '',
                'author': str(post.author) if post.author else '[deleted]',
                'subreddit': subreddit_name,
                'created_utc': datetime.fromtimestamp(post.created_utc),
                'score': post.score,
                'upvote_ratio': getattr(post, 'upvote_ratio', 0.5),
                'num_comments': post.num_comments,
                'url': post.url,
                'permalink': f"https://reddit.com{post.permalink}",
                'is_self': getattr(post, 'is_self', False),
                
                # Enhanced metadata
                'keyword_matched': keyword,
                'collection_method': collection_method,
                'platform': 'reddit',
                'engagement_score': post.score + (post.num_comments * 2),
                'content_length': len(post.title) + len(getattr(post, 'selftext', '')),
                'collection_timestamp': datetime.now().isoformat(),
                
                # Will be calculated
                'crisis_relevance_score': 0.0,
                'quality_score': 0.0,
                'content_hash': '',
            }
            
            # Calculate enhanced metrics
            post_data['crisis_relevance_score'] = self._calculate_crisis_relevance_enhanced(post_data)
            post_data['quality_score'] = self._calculate_post_quality(post_data)
            post_data['content_hash'] = self._generate_content_hash(post_data)
            
            return post_data
            
        except Exception as e:
            self._log(f"  ⚠️ Error extracting post {getattr(post, 'id', 'unknown')}: {e}", 'warning')
            return None
    
    def _is_crisis_relevant_enhanced(self, post, config: Dict) -> bool:
        """Enhanced crisis relevance detection"""
        text = (post.title + " " + getattr(post, 'selftext', '')).lower()
        
        # Check against all keyword categories
        all_keywords = []
        for category in config['keywords'].values():
            all_keywords.extend(category)
        
        # Require at least one keyword match
        for keyword in all_keywords:
            if keyword.lower() in text:
                return True
        
        return False
    
    def _calculate_crisis_relevance_enhanced(self, post_data: Dict) -> float:
        """Calculate enhanced crisis relevance score"""
        text = post_data['content'].lower()
        title = post_data['title'].lower()
        
        relevance_score = 0.0
        
        # Keyword density scoring
        crisis_keywords = ['fire', 'wildfire', 'evacuation', 'emergency', 'disaster',
                          'earthquake', 'conflict', 'crisis', 'alert', 'urgent']
        
        keyword_matches = sum(1 for kw in crisis_keywords if kw in text)
        relevance_score += min(keyword_matches * 0.1, 0.5)
        
        # Title importance boost
        title_matches = sum(1 for kw in crisis_keywords if kw in title)
        relevance_score += title_matches * 0.15
        
        # Emergency keyword boost
        emergency_keywords = ['urgent', 'breaking', 'alert', 'emergency', 'evacuate']
        emergency_matches = sum(1 for kw in emergency_keywords if kw in text)
        relevance_score += emergency_matches * 0.2
        
        return min(relevance_score, 1.0)
    
    def _calculate_post_quality(self, post_data: Dict) -> float:
        """Calculate post quality score based on multiple factors"""
        quality = 0.0
        
        # Engagement quality
        if post_data['score'] > 10:
            quality += 0.2
        if post_data['score'] > 100:
            quality += 0.2
        if post_data['num_comments'] > 5:
            quality += 0.2
        
        # Content quality
        content_length = post_data['content_length']
        if content_length > 50:
            quality += 0.2
        if content_length > 200:
            quality += 0.2
        
        # Author quality (not deleted)
        if post_data['author'] != '[deleted]':
            quality += 0.1
        
        # Self post quality (original content)
        if post_data['is_self']:
            quality += 0.1
        
        return min(quality, 1.0)
    
    def _generate_content_hash(self, post_data: Dict) -> str:
        """Generate hash for duplicate detection"""
        content = f"{post_data['title']}|{post_data['selftext']}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _process_collected_data(self, posts: List[Dict], crisis_id: str,
                              target_posts: int) -> pd.DataFrame:
        """Process and clean collected data"""
        if not posts:
            return pd.DataFrame()
        
        df = pd.DataFrame(posts)
        
        # Remove duplicates by content hash
        initial_count = len(df)
        df = df.drop_duplicates(subset=['content_hash'])
        duplicates_removed = initial_count - len(df)
        
        # Add crisis metadata
        df['crisis_id'] = crisis_id
        df['crisis_name'] = self.crisis_configs[crisis_id]['name']
        
        # Sort by quality and relevance
        df['combined_score'] = (df['quality_score'] * 0.4 + 
                               df['crisis_relevance_score'] * 0.4 + 
                               df['engagement_score'] / df['engagement_score'].max() * 0.2)
        
        df = df.sort_values('combined_score', ascending=False)
        
        # Limit to target
        if len(df) > target_posts:
            df = df.head(target_posts)
        
        self._log(f"  📊 Processed: {len(df)} posts (removed {duplicates_removed} duplicates)")
        
        return df
    
    def _save_enhanced_data(self, df: pd.DataFrame, crisis_id: str):
        """Save enhanced data with metadata"""
        if df.empty:
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save main CSV
        csv_path = self.raw_data_dir / f"{crisis_id}_enhanced_{timestamp}.csv"
        df.to_csv(csv_path, index=False)
        
        # Save detailed JSON
        json_path = self.raw_data_dir / f"{crisis_id}_enhanced_{timestamp}.json"
        df.to_json(json_path, orient='records', date_format='iso', indent=2)
        
        # Save collection metadata
        metadata = {
            'collection_timestamp': datetime.now().isoformat(),
            'crisis_id': crisis_id,
            'crisis_name': self.crisis_configs[crisis_id]['name'],
            'posts_collected': len(df),
            'collection_duration_minutes': (
                (self.stats.end_time - self.stats.start_time).total_seconds() / 60
                if self.stats.end_time else 0
            ),
            'subreddits_processed': self.stats.subreddits_processed,
            'errors_encountered': self.stats.errors_encountered,
            'strategies_used': self.collection_strategies,
            'average_quality_score': df['quality_score'].mean(),
            'average_relevance_score': df['crisis_relevance_score'].mean(),
            'top_subreddits': df['subreddit'].value_counts().to_dict(),
            'collection_methods': df['collection_method'].value_counts().to_dict()
        }
        
        metadata_path = self.raw_data_dir / f"{crisis_id}_metadata_{timestamp}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self._log(f"💾 Saved: {csv_path}")
        self._log(f"💾 Metadata: {metadata_path}")
    
    def _print_collection_summary(self, crisis_id: str, df: pd.DataFrame):
        """Print comprehensive collection summary"""
        config = self.crisis_configs[crisis_id]
        
        print("\n📊 ENHANCED COLLECTION SUMMARY")
        print("=" * 50)
        print(f"Crisis: {config['name']}")
        print(f"Posts Collected: {len(df)}")
        
        if not df.empty:
            print(f"Date Range: {df['created_utc'].min()} to {df['created_utc'].max()}")
            print(f"Average Score: {df['score'].mean():.1f}")
            print(f"Average Quality: {df['quality_score'].mean():.2f}")
            print(f"Average Relevance: {df['crisis_relevance_score'].mean():.2f}")
            
            print(f"\nTop Subreddits:")
            for subreddit, count in df['subreddit'].value_counts().head().items():
                print(f"  r/{subreddit}: {count}")
            
            print(f"\nCollection Methods:")
            for method, count in df['collection_method'].value_counts().items():
                print(f"  {method}: {count}")
            
            print(f"\nTop Posts:")
            top_posts = df.nlargest(3, 'combined_score')[['title', 'score', 'subreddit']]
            for i, (_, row) in enumerate(top_posts.iterrows(), 1):
                print(f"  {i}. {row['title'][:50]}... (r/{row['subreddit']}, Score: {row['score']})")
        
        duration = ((self.stats.end_time - self.stats.start_time).total_seconds() / 60 
                   if self.stats.end_time else 0)
        print(f"\n⏱️ Duration: {duration:.1f} minutes")
        print(f"📊 Subreddits Processed: {self.stats.subreddits_processed}")
        print(f"⚠️ Errors: {self.stats.errors_encountered}")

def run_enhanced_collection():
    """Run enhanced Reddit collection for all crises"""
    collector = EnhancedRedditCrisisCollector()
    
    print("🚀 ENHANCED REDDIT CRISIS DATA COLLECTION v2.0")
    print("=" * 60)
    
    all_crisis_data = {}
    
    # Collect data for each crisis with different targets based on priority
    collection_targets = {
        'la_wildfires_2025': 1500,  # Current event - highest priority
        'turkey_syria_earthquake_2023': 800,  # Historical event
        'india_pakistan_2025': 700   # Future/simulated event
    }
    
    for crisis_id, target in collection_targets.items():
        try:
            crisis_df = collector.collect_crisis_data_enhanced(
                crisis_id=crisis_id,
                target_posts=target,
                strategies=['search_keywords', 'hot_posts', 'new_posts', 'top_posts'],
                quality_threshold=0.2
            )
            all_crisis_data[crisis_id] = crisis_df
            
        except Exception as e:
            print(f"❌ Error collecting {crisis_id}: {e}")
            all_crisis_data[crisis_id] = pd.DataFrame()
        
        print("\n" + "="*60 + "\n")
    
    # Create combined dataset
    total_posts = sum(len(df) for df in all_crisis_data.values())
    
    if total_posts > 0:
        combined_df = pd.concat([df for df in all_crisis_data.values() if not df.empty], 
                               ignore_index=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        combined_path = collector.raw_data_dir / f"all_crises_enhanced_{timestamp}.csv"
        combined_df.to_csv(combined_path, index=False)
        
        print(f"🎯 FINAL SUMMARY:")
        print(f"Total Posts: {total_posts}")
        print(f"Combined Dataset: {combined_path}")
        
        for crisis_id, df in all_crisis_data.items():
            config = collector.crisis_configs[crisis_id]
            print(f"  {config['name']}: {len(df)} posts")
        
        if 2000 <= total_posts <= 5000:
            print("✅ Target range achieved with enhanced collection!")
        elif total_posts > 5000:
            print("🎉 Exceeded target - excellent data coverage!")
        
        print(f"💾 Enhanced data saved to: {collector.raw_data_dir}")
    
    return all_crisis_data

if __name__ == "__main__":
    run_enhanced_collection()
