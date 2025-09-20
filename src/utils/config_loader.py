"""
Configuration loader utility for Crisis Network Analysis Project
Handles loading of YAML configs, API keys, and project settings
"""

import yaml
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any, Optional
import logging

class ConfigLoader:
    """Centralized configuration management for the Crisis Network Analysis project"""
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize the configuration loader
        
        Args:
            config_dir (str): Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self._crisis_events_config = None
        self._analysis_params_config = None
        self._api_keys = None
        
        # Load environment variables from API keys file
        api_keys_path = self.config_dir / "api_keys.env"
        if api_keys_path.exists():
            load_dotenv(api_keys_path)
        else:
            logging.warning(f"API keys file not found: {api_keys_path}")
    
    def load_crisis_events(self) -> Dict[str, Any]:
        """
        Load crisis events configuration from YAML file
        
        Returns:
            Dict containing crisis events configuration
        """
        if self._crisis_events_config is None:
            config_path = self.config_dir / "crisis_events.yaml"
            
            try:
                with open(config_path, 'r', encoding='utf-8') as file:
                    self._crisis_events_config = yaml.safe_load(file)
                logging.info(f"Crisis events configuration loaded from {config_path}")
            except FileNotFoundError:
                logging.error(f"Crisis events configuration file not found: {config_path}")
                raise
            except yaml.YAMLError as e:
                logging.error(f"Error parsing crisis events YAML: {e}")
                raise
        
        return self._crisis_events_config
    
    def load_analysis_params(self) -> Dict[str, Any]:
        """
        Load analysis parameters configuration from YAML file
        
        Returns:
            Dict containing analysis parameters
        """
        if self._analysis_params_config is None:
            config_path = self.config_dir / "analysis_params.yaml"
            
            try:
                with open(config_path, 'r', encoding='utf-8') as file:
                    self._analysis_params_config = yaml.safe_load(file)
                logging.info(f"Analysis parameters loaded from {config_path}")
            except FileNotFoundError:
                logging.error(f"Analysis parameters file not found: {config_path}")
                raise
            except yaml.YAMLError as e:
                logging.error(f"Error parsing analysis parameters YAML: {e}")
                raise
        
        return self._analysis_params_config
    
    def get_api_keys(self) -> Dict[str, Dict[str, Optional[str]]]:
        """
        Get API keys from environment variables
        
        Returns:
            Dict containing API credentials for different services
        """
        if self._api_keys is None:
            self._api_keys = {
                'reddit': {
                    'client_id': os.getenv('REDDIT_CLIENT_ID'),
                    'client_secret': os.getenv('REDDIT_CLIENT_SECRET'),
                    'user_agent': os.getenv('REDDIT_USER_AGENT')
                },
                'twitter': {
                    'bearer_token': os.getenv('TWITTER_BEARER_TOKEN'),
                    'consumer_key': os.getenv('TWITTER_CONSUMER_KEY'),
                    'consumer_secret': os.getenv('TWITTER_CONSUMER_SECRET'),
                    'access_token': os.getenv('TWITTER_ACCESS_TOKEN'),
                    'access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
                },
                'news': {
                    'newsapi_key': os.getenv('NEWSAPI_KEY'),
                    'guardian_api_key': os.getenv('GUARDIAN_API_KEY')
                },
                'other': {
                    'openai_api_key': os.getenv('OPENAI_API_KEY'),
                    'google_api_key': os.getenv('GOOGLE_API_KEY')
                }
            }
        
        return self._api_keys
    
    def get_crisis_event_config(self, crisis_id: str) -> Dict[str, Any]:
        """
        Get configuration for a specific crisis event
        
        Args:
            crisis_id (str): Crisis event identifier
            
        Returns:
            Dict containing crisis event configuration
            
        Raises:
            KeyError: If crisis event not found
        """
        crisis_config = self.load_crisis_events()
        
        if crisis_id not in crisis_config['crisis_events']:
            available_crises = list(crisis_config['crisis_events'].keys())
            raise KeyError(f"Crisis event '{crisis_id}' not found. Available: {available_crises}")
        
        return crisis_config['crisis_events'][crisis_id]
    
    def get_global_settings(self) -> Dict[str, Any]:
        """
        Get global project settings
        
        Returns:
            Dict containing global configuration settings
        """
        crisis_config = self.load_crisis_events()
        return crisis_config.get('global_settings', {})
    
    def get_reddit_subreddits(self, crisis_id: str) -> list:
        """
        Get Reddit subreddits for a specific crisis event
        
        Args:
            crisis_id (str): Crisis event identifier
            
        Returns:
            List of subreddit names for the crisis
        """
        crisis_config = self.get_crisis_event_config(crisis_id)
        return crisis_config.get('platforms', {}).get('reddit', {}).get('subreddits', [])
    
    def get_crisis_keywords(self, crisis_id: str, category: str = 'primary') -> list:
        """
        Get keywords for a specific crisis event
        
        Args:
            crisis_id (str): Crisis event identifier
            category (str): Keyword category ('primary', 'secondary', etc.)
            
        Returns:
            List of keywords for the specified category
        """
        crisis_config = self.get_crisis_event_config(crisis_id)
        keywords = crisis_config.get('keywords', {})
        
        if category in keywords:
            return keywords[category]
        else:
            # Return all keywords flattened if category not found
            all_keywords = []
            for keyword_list in keywords.values():
                if isinstance(keyword_list, list):
                    all_keywords.extend(keyword_list)
            return all_keywords
    
    def get_crisis_date_range(self, crisis_id: str, include_buffer: bool = True) -> tuple:
        """
        Get date range for a crisis event
        
        Args:
            crisis_id (str): Crisis event identifier
            include_buffer (bool): Whether to include pre/post crisis buffer days
            
        Returns:
            Tuple of (start_date, end_date) as strings
        """
        crisis_config = self.get_crisis_event_config(crisis_id)
        start_date = crisis_config['start_date']
        end_date = crisis_config['end_date']
        
        if include_buffer:
            global_settings = self.get_global_settings()
            data_collection = global_settings.get('data_collection', {})
            
            # Add buffer days if configured
            pre_buffer = data_collection.get('pre_crisis_buffer_days', 0)
            post_buffer = data_collection.get('post_crisis_buffer_days', 0)
            
            # Note: In production, you'd want to add proper date arithmetic here
            # For now, returning the basic dates
        
        return start_date, end_date
    
    def validate_api_keys(self, service: str) -> bool:
        """
        Validate that required API keys are present for a service
        
        Args:
            service (str): Service name ('reddit', 'twitter', 'news')
            
        Returns:
            bool: True if required keys are present
        """
        api_keys = self.get_api_keys()
        
        if service == 'reddit':
            required_keys = ['client_id', 'client_secret', 'user_agent']
            reddit_keys = api_keys.get('reddit', {})
            return all(reddit_keys.get(key) is not None for key in required_keys)
        
        elif service == 'twitter':
            twitter_keys = api_keys.get('twitter', {})
            # Check if at least bearer token is present
            return twitter_keys.get('bearer_token') is not None
        
        elif service == 'news':
            news_keys = api_keys.get('news', {})
            # Check if at least one news API key is present
            return (news_keys.get('newsapi_key') is not None or 
                   news_keys.get('guardian_api_key') is not None)
        
        return False
    
    def get_analysis_parameter(self, parameter_path: str, default=None):
        """
        Get a specific analysis parameter using dot notation
        
        Args:
            parameter_path (str): Parameter path like 'resonance_plus.window_size_minutes'
            default: Default value if parameter not found
            
        Returns:
            Parameter value or default
        """
        params = self.load_analysis_params()
        
        # Navigate through nested dictionary using dot notation
        keys = parameter_path.split('.')
        current = params.get('analysis_parameters', {})
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current

# Global configuration loader instance
config_loader = ConfigLoader()

def get_config() -> ConfigLoader:
    """
    Get the global configuration loader instance
    
    Returns:
        ConfigLoader: Global configuration loader
    """
    return config_loader
