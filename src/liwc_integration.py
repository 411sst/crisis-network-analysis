"""
LIWC Integration Framework for Crisis Network Analysis
Implements cognitive and perceptual process analysis to enhance network resilience metrics

Based on Wang & Kogan (2025) Resonance+ methodology and PADM framework integration
"""

import pandas as pd
import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Optional, Union
import json
from pathlib import Path
from datetime import datetime
import re
from collections import defaultdict, Counter
from sklearn.preprocessing import StandardScaler
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class LIWCCrisisAnalyzer:
    """
    Enhanced LIWC analyzer for crisis network analysis with PADM integration
    Implements cognitive and perceptual process analysis for emergency management
    """
    
    def __init__(self, network_analyzer=None):
        """
        Initialize LIWC Crisis Analyzer
        
        Args:
            network_analyzer: Existing CrisisNetworkAnalyzer instance
        """
        self.network_analyzer = network_analyzer
        self.liwc_categories = self._initialize_liwc_categories()
        self.base_rates = {}
        self.cognitive_profiles = {}
        self.resonance_scores = {}
        
    def _initialize_liwc_categories(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Initialize LIWC categories for crisis analysis
        Based on Wang & Kogan (2025) methodology
        """
        return {
            # Cognitive Processes - Core PADM Components
            'cognitive_processes': {
                'cogproc': ['think', 'know', 'consider', 'understand', 'realize', 'believe', 
                          'remember', 'analyze', 'decide', 'conclude', 'reason', 'logic'],
                'causation': ['because', 'cause', 'due', 'since', 'reason', 'why', 'effect', 
                            'result', 'lead', 'influence', 'impact', 'consequence'],
                'certainty': ['sure', 'certain', 'definitely', 'absolutely', 'clearly', 'obvious',
                            'undoubtedly', 'without', 'doubt', 'guarantee', 'confirm'],
                'differentiation': ['but', 'however', 'although', 'whereas', 'different', 
                                  'distinguish', 'contrast', 'unlike', 'except', 'rather'],
                'discrepancies': ['should', 'would', 'could', 'wish', 'hope', 'need', 'want',
                                'expect', 'better', 'worse', 'improve', 'change'],
                'insight': ['understand', 'realize', 'see', 'recognize', 'aware', 'discover',
                          'learn', 'find', 'notice', 'grasp', 'comprehend', 'insight'],
                'tentative': ['maybe', 'perhaps', 'might', 'possibly', 'probably', 'seem',
                            'appear', 'guess', 'suppose', 'suggest', 'uncertain'],
                'comparison': ['more', 'less', 'than', 'compare', 'similar', 'same', 'like',
                             'unlike', 'equal', 'versus', 'between', 'among']
            },
            
            # Perceptual Processes - PADM Attention Component
            'perceptual_processes': {
                'percept': ['see', 'hear', 'feel', 'touch', 'taste', 'smell', 'look', 'watch',
                          'listen', 'observe', 'notice', 'sense', 'perceive'],
                'see': ['see', 'saw', 'seen', 'look', 'watch', 'observe', 'notice', 'view',
                       'witness', 'spot', 'glimpse', 'stare', 'gaze', 'glance'],
                'hear': ['hear', 'heard', 'listen', 'sound', 'noise', 'voice', 'music',
                        'loud', 'quiet', 'silent', 'whisper', 'shout', 'scream'],
                'feel': ['feel', 'felt', 'touch', 'warm', 'cold', 'hot', 'cool', 'smooth',
                        'rough', 'soft', 'hard', 'pain', 'hurt', 'comfort']
            },
            
            # Emotional Processes - PADM Risk Perception
            'emotional_processes': {
                'affect': ['happy', 'sad', 'angry', 'fear', 'joy', 'love', 'hate', 'worry',
                          'excited', 'nervous', 'calm', 'anxious', 'pleased', 'upset'],
                'posemo': ['happy', 'joy', 'love', 'nice', 'good', 'great', 'excellent',
                          'wonderful', 'amazing', 'perfect', 'beautiful', 'smile', 'laugh'],
                'negemo': ['sad', 'angry', 'hate', 'terrible', 'awful', 'bad', 'worst',
                          'horrible', 'disgusting', 'evil', 'nasty', 'ugly', 'cry'],
                'anx': ['worry', 'fear', 'nervous', 'anxious', 'scared', 'afraid', 'panic',
                       'stress', 'tension', 'concern', 'trouble', 'problem', 'crisis'],
                'anger': ['angry', 'mad', 'hate', 'furious', 'rage', 'irritated', 'annoyed',
                         'frustrated', 'pissed', 'damn', 'fight', 'argue', 'attack'],
                'sad': ['sad', 'cry', 'grief', 'sorrow', 'tears', 'depressed', 'miserable',
                       'unhappy', 'lonely', 'hurt', 'pain', 'loss', 'death'],
                'swear': ['damn', 'hell', 'shit', 'fuck', 'ass', 'bitch', 'bastard',
                         'crap', 'piss', 'suck', 'wtf', 'omg', 'jesus']
            },
            
            # Behavioral Responses - PADM Action Component
            'behavioral_responses': {
                'risk': ['danger', 'risk', 'threat', 'warning', 'alert', 'emergency', 'crisis',
                        'hazard', 'unsafe', 'careful', 'caution', 'avoid', 'escape'],
                'social': ['we', 'us', 'our', 'they', 'them', 'their', 'people', 'community',
                          'together', 'help', 'support', 'share', 'connect', 'family'],
                'work': ['work', 'job', 'office', 'business', 'company', 'employee', 'boss',
                        'meeting', 'project', 'task', 'duty', 'responsibility'],
                'leisure': ['fun', 'play', 'game', 'sport', 'entertainment', 'vacation', 
                           'holiday', 'party', 'celebration', 'enjoy', 'relax'],
                'home': ['home', 'house', 'family', 'kitchen', 'bedroom', 'room', 'apartment',
                        'neighborhood', 'domestic', 'household', 'yard', 'garden'],
                'money': ['money', 'dollar', 'cost', 'expensive', 'cheap', 'buy', 'sell',
                         'pay', 'price', 'budget', 'financial', 'economic', 'tax'],
                'death': ['death', 'die', 'dead', 'kill', 'murder', 'suicide', 'grave',
                         'funeral', 'cemetery', 'victim', 'casualty', 'fatality'],
                'time': ['time', 'hour', 'minute', 'day', 'week', 'month', 'year', 'now',
                        'today', 'tomorrow', 'yesterday', 'soon', 'late', 'early'],
                'space': ['here', 'there', 'where', 'place', 'location', 'area', 'region',
                         'city', 'country', 'north', 'south', 'east', 'west', 'near'],
                'motion': ['go', 'move', 'come', 'run', 'walk', 'drive', 'fly', 'travel',
                          'leave', 'arrive', 'return', 'follow', 'chase', 'escape']
            }
        }
    
    def calculate_liwc_scores(self, text: str) -> Dict[str, float]:
        """
        Calculate LIWC scores for a given text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary of LIWC category scores
        """
        if pd.isna(text) or not isinstance(text, str):
            return {cat: 0.0 for cat_group in self.liwc_categories.values() 
                    for cat in cat_group.keys()}
        
        # Preprocess text
        text = text.lower()
        words = re.findall(r'\b\w+\b', text)
        total_words = len(words)
        
        if total_words == 0:
            return {cat: 0.0 for cat_group in self.liwc_categories.values() 
                    for cat in cat_group.keys()}
        
        # Calculate scores for each category
        scores = {}
        for category_group in self.liwc_categories.values():
            for category, word_list in category_group.items():
                matches = sum(1 for word in words if word in word_list)
                scores[category] = (matches / total_words) * 100
        
        return scores
    
    def analyze_dataset_liwc(self, df: pd.DataFrame, text_column: str = 'content') -> pd.DataFrame:
        """
        Analyze entire dataset with LIWC scoring
        
        Args:
            df: DataFrame with text data
            text_column: Column name containing text to analyze
            
        Returns:
            DataFrame with LIWC scores added
        """
        print(f"Calculating LIWC scores for {len(df)} posts...")
        
        # Calculate LIWC scores for each post
        liwc_scores = []
        for idx, row in df.iterrows():
            if idx % 500 == 0:
                print(f"Processed {idx}/{len(df)} posts")
            
            scores = self.calculate_liwc_scores(row[text_column])
            liwc_scores.append(scores)
        
        # Convert to DataFrame and merge
        liwc_df = pd.DataFrame(liwc_scores)
        
        # Add LIWC columns to original DataFrame
        df_with_liwc = pd.concat([df, liwc_df], axis=1)
        
        # Calculate base rates for normalization
        self._calculate_base_rates(liwc_df)
        
        print("LIWC analysis completed!")
        return df_with_liwc
    
    def _calculate_base_rates(self, liwc_df: pd.DataFrame):
        """Calculate empirical base rates for LIWC categories"""
        self.base_rates = {}
        for category in liwc_df.columns:
            # Use median instead of mean to be robust to outliers
            self.base_rates[category] = liwc_df[category].median()
    
    def calculate_normalized_liwc_scores(self, df: pd.DataFrame, 
                                       group_column: str = 'crisis_id') -> pd.DataFrame:
        """
        Calculate Normalized LIWC Scores (NLS) following Wang & Kogan methodology
        
        Args:
            df: DataFrame with LIWC scores
            group_column: Column to group by for normalization
            
        Returns:
            DataFrame with normalized scores
        """
        liwc_columns = [col for col in df.columns if col in 
                       [cat for cat_group in self.liwc_categories.values() 
                        for cat in cat_group.keys()]]
        
        normalized_df = df.copy()
        
        for category in liwc_columns:
            base_rate = self.base_rates.get(category, df[category].median())
            if base_rate > 0:
                # NLS = (score - base_rate) / base_rate * 100
                normalized_df[f'{category}_nls'] = ((df[category] - base_rate) / base_rate) * 100
            else:
                normalized_df[f'{category}_nls'] = 0
        
        return normalized_df
    
    def calculate_resonance_plus(self, df: pd.DataFrame, 
                               network_metrics: Dict) -> pd.DataFrame:
        """
        Calculate Resonance+ scores integrating LIWC with network metrics
        
        Components:
        1. In-conversation Novelty
        2. Local Persistence  
        3. Crisis Relevance
        4. Cognitive Resonance (LIWC-based)
        
        Args:
            df: DataFrame with LIWC scores and network data
            network_metrics: Network metrics from previous analysis
            
        Returns:
            DataFrame with Resonance+ scores
        """
        print("Calculating Resonance+ scores...")
        
        df_resonance = df.copy()
        
        # Component 1: In-conversation Novelty (based on content uniqueness)
        df_resonance['novelty_score'] = self._calculate_novelty_score(df_resonance)
        
        # Component 2: Local Persistence (based on engagement)
        df_resonance['persistence_score'] = self._calculate_persistence_score(df_resonance)
        
        # Component 3: Crisis Relevance (LIWC-based)
        df_resonance['crisis_relevance'] = self._calculate_crisis_relevance(df_resonance)
        
        # Component 4: Cognitive Resonance (LIWC cognitive processes)
        df_resonance['cognitive_resonance'] = self._calculate_cognitive_resonance(df_resonance)
        
        # Calculate final Resonance+ score
        df_resonance['resonance_plus'] = (
            0.25 * df_resonance['novelty_score'] +
            0.25 * df_resonance['persistence_score'] +
            0.25 * df_resonance['crisis_relevance'] +
            0.25 * df_resonance['cognitive_resonance']
        )
        
        # Normalize to 0-1 scale
        scaler = StandardScaler()
        df_resonance['resonance_plus_normalized'] = scaler.fit_transform(
            df_resonance[['resonance_plus']]
        ).flatten()
        
        print("Resonance+ calculation completed!")
        return df_resonance
    
    def _calculate_novelty_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate in-conversation novelty based on content similarity"""
        # Simple implementation: inverse of content repetition
        content_counts = df['content'].value_counts()
        novelty_scores = df['content'].map(lambda x: 1.0 / content_counts[x])
        return novelty_scores
    
    def _calculate_persistence_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate local persistence based on engagement metrics"""
        engagement_cols = ['upvotes', 'comments', 'shares']
        available_cols = [col for col in engagement_cols if col in df.columns]
        
        if available_cols:
            # Combine available engagement metrics
            engagement_sum = df[available_cols].fillna(0).sum(axis=1)
            # Log transform to handle large values
            persistence = np.log1p(engagement_sum)
        else:
            # Fallback: use content length as proxy
            persistence = np.log1p(df['content'].str.len().fillna(0))
        
        return persistence
    
    def _calculate_crisis_relevance(self, df: pd.DataFrame) -> pd.Series:
        """Calculate crisis relevance using LIWC risk and emotion categories"""
        relevance_categories = ['risk', 'anx', 'negemo', 'time', 'space', 'motion']
        available_categories = [cat for cat in relevance_categories if cat in df.columns]
        
        if available_categories:
            crisis_relevance = df[available_categories].sum(axis=1)
        else:
            # Fallback: basic keyword matching
            crisis_keywords = ['emergency', 'crisis', 'disaster', 'danger', 'help', 
                             'urgent', 'warning', 'alert', 'evacuation', 'rescue']
            crisis_relevance = df['content'].str.lower().str.count('|'.join(crisis_keywords))
        
        return crisis_relevance
    
    def _calculate_cognitive_resonance(self, df: pd.DataFrame) -> pd.Series:
        """Calculate cognitive resonance using LIWC cognitive process categories"""
        cognitive_categories = ['cogproc', 'insight', 'certainty', 'causation']
        available_categories = [cat for cat in cognitive_categories if cat in df.columns]
        
        if available_categories:
            cognitive_resonance = df[available_categories].sum(axis=1)
        else:
            # Fallback: simple cognitive keyword matching
            cognitive_keywords = ['think', 'know', 'understand', 'realize', 'because', 
                                'reason', 'cause', 'sure', 'certain', 'insight']
            cognitive_resonance = df['content'].str.lower().str.count('|'.join(cognitive_keywords))
        
        return cognitive_resonance
    
    def generate_padm_analysis(self, df: pd.DataFrame) -> Dict:
        """
        Generate PADM framework analysis using LIWC scores
        
        PADM Components:
        - Exposure: Perceptual processes
        - Attention: Cognitive processes + comparison
        - Comprehension: Insight + certainty
        """
        padm_analysis = {
            'exposure_metrics': self._analyze_exposure(df),
            'attention_metrics': self._analyze_attention(df),
            'comprehension_metrics': self._analyze_comprehension(df),
            'summary_statistics': self._padm_summary_stats(df)
        }
        
        return padm_analysis
    
    def _analyze_exposure(self, df: pd.DataFrame) -> Dict:
        """Analyze PADM Exposure component using perceptual processes"""
        exposure_categories = ['percept', 'see', 'hear', 'feel']
        available_categories = [cat for cat in exposure_categories if cat in df.columns]
        
        if not available_categories:
            return {'warning': 'No perceptual process data available'}
        
        exposure_metrics = {}
        for category in available_categories:
            exposure_metrics[category] = {
                'mean': df[category].mean(),
                'median': df[category].median(),
                'std': df[category].std(),
                'high_exposure_posts': (df[category] > df[category].quantile(0.9)).sum()
            }
        
        # Calculate overall exposure score
        exposure_scores = df[available_categories].mean(axis=1)
        exposure_metrics['overall_exposure'] = {
            'mean': exposure_scores.mean(),
            'high_exposure_threshold': exposure_scores.quantile(0.9),
            'posts_above_threshold': (exposure_scores > exposure_scores.quantile(0.9)).sum()
        }
        
        return exposure_metrics
    
    def _analyze_attention(self, df: pd.DataFrame) -> Dict:
        """Analyze PADM Attention component using cognitive processes"""
        attention_categories = ['cogproc', 'comparison', 'differentiation']
        available_categories = [cat for cat in attention_categories if cat in df.columns]
        
        if not available_categories:
            return {'warning': 'No cognitive process data available'}
        
        attention_metrics = {}
        for category in available_categories:
            attention_metrics[category] = {
                'mean': df[category].mean(),
                'median': df[category].median(),
                'std': df[category].std(),
                'high_attention_posts': (df[category] > df[category].quantile(0.9)).sum()
            }
        
        # Calculate overall attention score
        attention_scores = df[available_categories].mean(axis=1)
        attention_metrics['overall_attention'] = {
            'mean': attention_scores.mean(),
            'high_attention_threshold': attention_scores.quantile(0.9),
            'posts_above_threshold': (attention_scores > attention_scores.quantile(0.9)).sum()
        }
        
        return attention_metrics
    
    def _analyze_comprehension(self, df: pd.DataFrame) -> Dict:
        """Analyze PADM Comprehension component using insight and certainty"""
        comprehension_categories = ['insight', 'certainty', 'causation']
        available_categories = [cat for cat in comprehension_categories if cat in df.columns]
        
        if not available_categories:
            return {'warning': 'No comprehension process data available'}
        
        comprehension_metrics = {}
        for category in available_categories:
            comprehension_metrics[category] = {
                'mean': df[category].mean(),
                'median': df[category].median(),
                'std': df[category].std(),
                'high_comprehension_posts': (df[category] > df[category].quantile(0.9)).sum()
            }
        
        # Calculate overall comprehension score
        comprehension_scores = df[available_categories].mean(axis=1)
        comprehension_metrics['overall_comprehension'] = {
            'mean': comprehension_scores.mean(),
            'high_comprehension_threshold': comprehension_scores.quantile(0.9),
            'posts_above_threshold': (comprehension_scores > comprehension_scores.quantile(0.9)).sum()
        }
        
        return comprehension_metrics
    
    def _padm_summary_stats(self, df: pd.DataFrame) -> Dict:
        """Calculate summary statistics for PADM analysis"""
        return {
            'total_posts_analyzed': len(df),
            'crisis_events': df['crisis_id'].nunique() if 'crisis_id' in df.columns else 'Unknown',
            'analysis_timestamp': datetime.now().isoformat(),
            'liwc_categories_available': [col for col in df.columns if col in 
                                        [cat for cat_group in self.liwc_categories.values() 
                                         for cat in cat_group.keys()]]
        }
    
    def conduct_statistical_analysis(self, df: pd.DataFrame) -> Dict:
        """
        Conduct statistical analysis comparing LIWC scores across crisis types
        Following Wang & Kogan methodology with two-proportion z-tests
        """
        if 'crisis_id' not in df.columns:
            return {'error': 'Crisis ID column not found'}
        
        liwc_columns = [col for col in df.columns if col in 
                       [cat for cat_group in self.liwc_categories.values() 
                        for cat in cat_group.keys()]]
        
        if not liwc_columns:
            return {'error': 'No LIWC scores found in dataset'}
        
        crisis_types = df['crisis_id'].unique()
        statistical_results = {}
        
        # Pairwise comparisons between crisis types
        for i, crisis1 in enumerate(crisis_types):
            for crisis2 in crisis_types[i+1:]:
                comparison_key = f"{crisis1}_vs_{crisis2}"
                statistical_results[comparison_key] = {}
                
                df1 = df[df['crisis_id'] == crisis1]
                df2 = df[df['crisis_id'] == crisis2]
                
                for category in liwc_columns:
                    # Two-proportion z-test (Wang & Kogan methodology)
                    try:
                        # Convert scores to binary (above median = 1, below = 0)
                        threshold = df[category].median()
                        
                        count1 = (df1[category] > threshold).sum()
                        count2 = (df2[category] > threshold).sum()
                        
                        n1, n2 = len(df1), len(df2)
                        
                        if n1 > 0 and n2 > 0:
                            # Calculate proportions
                            p1, p2 = count1/n1, count2/n2
                            
                            # Pooled proportion
                            p_pooled = (count1 + count2) / (n1 + n2)
                            
                            # Standard error
                            se = np.sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2))
                            
                            if se > 0:
                                # Z-score
                                z_score = (p1 - p2) / se
                                
                                # P-value (two-tailed)
                                p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
                                
                                statistical_results[comparison_key][category] = {
                                    'proportion_1': p1,
                                    'proportion_2': p2,
                                    'z_score': z_score,
                                    'p_value': p_value,
                                    'significant': p_value < 0.05,
                                    'sample_sizes': [n1, n2]
                                }
                    except Exception as e:
                        statistical_results[comparison_key][category] = {
                            'error': str(e)
                        }
        
        return statistical_results
    
    def generate_crisis_profiles(self, df: pd.DataFrame) -> Dict:
        """
        Generate cognitive and emotional profiles for each crisis type
        """
        if 'crisis_id' not in df.columns:
            return {'error': 'Crisis ID column not found'}
        
        liwc_columns = [col for col in df.columns if col in 
                       [cat for cat_group in self.liwc_categories.values() 
                        for cat in cat_group.keys()]]
        
        crisis_profiles = {}
        
        for crisis_id in df['crisis_id'].unique():
            crisis_data = df[df['crisis_id'] == crisis_id]
            
            profile = {
                'basic_stats': {
                    'total_posts': len(crisis_data),
                    'unique_authors': crisis_data['author'].nunique() if 'author' in crisis_data.columns else 'Unknown',
                    'date_range': {
                        'start': crisis_data['created_utc'].min() if 'created_utc' in crisis_data.columns else None,
                        'end': crisis_data['created_utc'].max() if 'created_utc' in crisis_data.columns else None
                    }
                },
                'cognitive_profile': {},
                'emotional_profile': {},
                'behavioral_profile': {},
                'perceptual_profile': {}
            }
            
            # Cognitive processes
            cognitive_cats = ['cogproc', 'causation', 'certainty', 'insight', 'tentative']
            for cat in cognitive_cats:
                if cat in crisis_data.columns:
                    profile['cognitive_profile'][cat] = {
                        'mean': crisis_data[cat].mean(),
                        'median': crisis_data[cat].median(),
                        'std': crisis_data[cat].std(),
                        'percentile_75': crisis_data[cat].quantile(0.75),
                        'percentile_90': crisis_data[cat].quantile(0.90)
                    }
            
            # Emotional processes
            emotional_cats = ['affect', 'posemo', 'negemo', 'anx', 'anger', 'sad']
            for cat in emotional_cats:
                if cat in crisis_data.columns:
                    profile['emotional_profile'][cat] = {
                        'mean': crisis_data[cat].mean(),
                        'median': crisis_data[cat].median(),
                        'std': crisis_data[cat].std(),
                        'percentile_75': crisis_data[cat].quantile(0.75),
                        'percentile_90': crisis_data[cat].quantile(0.90)
                    }
            
            # Behavioral responses
            behavioral_cats = ['risk', 'social', 'time', 'space', 'motion']
            for cat in behavioral_cats:
                if cat in crisis_data.columns:
                    profile['behavioral_profile'][cat] = {
                        'mean': crisis_data[cat].mean(),
                        'median': crisis_data[cat].median(),
                        'std': crisis_data[cat].std(),
                        'percentile_75': crisis_data[cat].quantile(0.75),
                        'percentile_90': crisis_data[cat].quantile(0.90)
                    }
            
            # Perceptual processes
            perceptual_cats = ['percept', 'see', 'hear', 'feel']
            for cat in perceptual_cats:
                if cat in crisis_data.columns:
                    profile['perceptual_profile'][cat] = {
                        'mean': crisis_data[cat].mean(),
                        'median': crisis_data[cat].median(),
                        'std': crisis_data[cat].std(),
                        'percentile_75': crisis_data[cat].quantile(0.75),
                        'percentile_90': crisis_data[cat].quantile(0.90)
                    }
            
            crisis_profiles[crisis_id] = profile
        
        return crisis_profiles
    
    def identify_cognitive_hubs(self, df: pd.DataFrame, network_hubs: Dict) -> Dict:
        """
        Identify cognitive hubs by combining network analysis with LIWC scores
        Enhanced hub classification using cognitive processes
        """
        if 'resonance_plus' not in df.columns:
            print("Warning: Resonance+ scores not found. Calculate them first.")
            return {}
        
        cognitive_hubs = {
            'cognitive_influencers': [],      # High cognitive processes + network centrality
            'emotional_resonators': [],       # High emotional processes + engagement
            'information_synthesizers': [],   # High insight + causation + network bridges
            'risk_communicators': [],        # High risk language + network reach
            'community_coordinators': [],    # High social language + network clustering
            'crisis_specialists': []         # High crisis relevance + domain expertise
        }
        
        # Get top posts by different criteria
        top_percentile = 0.90
        
        # Cognitive Influencers: High cognitive processes + network metrics
        cognitive_cats = ['cogproc', 'insight', 'causation', 'certainty']
        available_cognitive = [cat for cat in cognitive_cats if cat in df.columns]
        
        if available_cognitive:
            df['cognitive_score'] = df[available_cognitive].mean(axis=1)
            cognitive_threshold = df['cognitive_score'].quantile(top_percentile)
            
            cognitive_influencers = df[
                (df['cognitive_score'] > cognitive_threshold) &
                (df['resonance_plus'] > df['resonance_plus'].quantile(0.8))
            ]['post_id'].tolist() if 'post_id' in df.columns else df.index.tolist()
            
            cognitive_hubs['cognitive_influencers'] = cognitive_influencers[:10]
        
        # Emotional Resonators: High emotional language
        emotional_cats = ['affect', 'posemo', 'negemo', 'anx']
        available_emotional = [cat for cat in emotional_cats if cat in df.columns]
        
        if available_emotional:
            df['emotional_score'] = df[available_emotional].mean(axis=1)
            emotional_threshold = df['emotional_score'].quantile(top_percentile)
            
            emotional_resonators = df[
                df['emotional_score'] > emotional_threshold
            ]['post_id'].tolist() if 'post_id' in df.columns else df.index.tolist()
            
            cognitive_hubs['emotional_resonators'] = emotional_resonators[:10]
        
        # Risk Communicators: High risk language
        if 'risk' in df.columns and 'anx' in df.columns:
            df['risk_communication_score'] = df['risk'] + df['anx']
            risk_threshold = df['risk_communication_score'].quantile(top_percentile)
            
            risk_communicators = df[
                df['risk_communication_score'] > risk_threshold
            ]['post_id'].tolist() if 'post_id' in df.columns else df.index.tolist()
            
            cognitive_hubs['risk_communicators'] = risk_communicators[:10]
        
        # Community Coordinators: High social language
        if 'social' in df.columns:
            social_threshold = df['social'].quantile(top_percentile)
            
            community_coordinators = df[
                df['social'] > social_threshold
            ]['post_id'].tolist() if 'post_id' in df.columns else df.index.tolist()
            
            cognitive_hubs['community_coordinators'] = community_coordinators[:10]
        
        return cognitive_hubs
    
    def save_analysis_results(self, df: pd.DataFrame, output_dir: str = 'results/liwc'):
        """
        Save LIWC analysis results to files
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save enhanced dataset with LIWC scores
        liwc_file = output_path / f'liwc_enhanced_dataset_{timestamp}.csv'
        df.to_csv(liwc_file, index=False)
        
        # Generate and save crisis profiles
        crisis_profiles = self.generate_crisis_profiles(df)
        profiles_file = output_path / f'crisis_cognitive_profiles_{timestamp}.json'
        with open(profiles_file, 'w') as f:
            json.dump(crisis_profiles, f, indent=2, default=str)
        
        # Generate and save PADM analysis
        padm_analysis = self.generate_padm_analysis(df)
        padm_file = output_path / f'padm_analysis_{timestamp}.json'
        with open(padm_file, 'w') as f:
            json.dump(padm_analysis, f, indent=2, default=str)
        
        # Generate and save statistical analysis
        statistical_results = self.conduct_statistical_analysis(df)
        stats_file = output_path / f'statistical_analysis_{timestamp}.json'
        with open(stats_file, 'w') as f:
            json.dump(statistical_results, f, indent=2, default=str)
        
        # Save summary report
        summary_file = output_path / f'liwc_analysis_summary_{timestamp}.txt'
        with open(summary_file, 'w') as f:
            f.write(f"LIWC Crisis Network Analysis Report\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write(f"Dataset: {len(df)} total posts\n\n")
            
            f.write("Files Generated:\n")
            f.write(f"  Enhanced Dataset: {liwc_file.name}\n")
            f.write(f"  Crisis Profiles: {profiles_file.name}\n")
            f.write(f"  PADM Analysis: {padm_file.name}\n")
            f.write(f"  Statistical Analysis: {stats_file.name}\n")
        
        print(f"LIWC analysis results saved to {output_path}")
        return {
            'enhanced_dataset': str(liwc_file),
            'crisis_profiles': str(profiles_file),
            'padm_analysis': str(padm_file),
            'statistical_analysis': str(stats_file),
            'summary_report': str(summary_file)
        }

# Usage Example and Integration Function
def integrate_liwc_with_existing_analysis(data_file: str, network_results_dir: str):
    """
    Integration function to combine LIWC analysis with existing network results
    
    Args:
        data_file: Path to the original dataset CSV
        network_results_dir: Directory containing network analysis results
    """
    print("🧠 Starting LIWC Integration with Crisis Network Analysis")
    
    # Load original dataset
    print("📊 Loading dataset...")
    df = pd.read_csv(data_file)
    
    # Initialize LIWC analyzer
    liwc_analyzer = LIWCCrisisAnalyzer()
    
    # Step 1: Calculate LIWC scores
    print("🔍 Calculating LIWC scores...")
    df_with_liwc = liwc_analyzer.analyze_dataset_liwc(df)
    
    # Step 2: Calculate normalized scores
    print("📈 Calculating normalized LIWC scores...")
    df_normalized = liwc_analyzer.calculate_normalized_liwc_scores(df_with_liwc)
    
    # Step 3: Load network metrics if available
    network_metrics = {}
    network_results_path = Path(network_results_dir)
    if network_results_path.exists():
        # Look for network metrics files
        for metrics_file in network_results_path.glob("*network_metrics*.json"):
            with open(metrics_file, 'r') as f:
                network_metrics.update(json.load(f))
    
    # Step 4: Calculate Resonance+ scores
    print("⭐ Calculating Resonance+ scores...")
    df_final = liwc_analyzer.calculate_resonance_plus(df_normalized, network_metrics)
    
    # Step 5: Generate comprehensive analysis
    print("📋 Generating PADM analysis...")
    padm_results = liwc_analyzer.generate_padm_analysis(df_final)
    
    # Step 6: Statistical analysis
    print("📊 Conducting statistical analysis...")
    statistical_results = liwc_analyzer.conduct_statistical_analysis(df_final)
    
    # Step 7: Save all results
    print("💾 Saving results...")
    file_paths = liwc_analyzer.save_analysis_results(df_final)
    
    print("✅ LIWC Integration Complete!")
    print("\nGenerated Files:")
    for file_type, file_path in file_paths.items():
        print(f"  {file_type}: {file_path}")
    
    return df_final, padm_results, statistical_results

# Fish shell compatible usage instructions
"""
FISH SHELL USAGE INSTRUCTIONS:

# 1. Navigate to your project directory
cd /path/to/crisis-network-analysis

# 2. Activate your Python environment
source venv/bin/activate.fish

# 3. Run the LIWC integration in Python:
python -c "
from liwc_integration import integrate_liwc_with_existing_analysis
df, padm, stats = integrate_liwc_with_existing_analysis(
    'data/collected/combined_crisis_data.csv',
    'results/networks'
)
print('LIWC Integration completed!')
"

# 4. Or create a simple script:
echo '#!/usr/bin/env python3
import sys
sys.path.append(".")
from liwc_integration import integrate_liwc_with_existing_analysis

df, padm, stats = integrate_liwc_with_existing_analysis(
    "data/collected/combined_crisis_data.csv", 
    "results/networks"
)
print("Analysis complete!")
' > run_liwc_analysis.py

chmod +x run_liwc_analysis.py
python run_liwc_analysis.py
"""