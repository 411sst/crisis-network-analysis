"""
Logging utility for Crisis Network Analysis Project
Provides structured logging across all project modules
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Union
import json

class CrisisLogger:
    """Enhanced logger for crisis network analysis with structured logging"""
    
    def __init__(self, 
                 name: str,
                 log_level: str = "INFO",
                 log_to_file: bool = True,
                 log_to_console: bool = True,
                 log_dir: str = "logs"):
        """
        Initialize the crisis logger
        
        Args:
            name (str): Logger name (usually module name)
            log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file (bool): Whether to log to file
            log_to_console (bool): Whether to log to console
            log_dir (str): Directory for log files
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # File handler
        if log_to_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = self.log_dir / f"{name}_{timestamp}.log"
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(file_handler)
        
        # Console handler
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, log_level.upper()))
            console_handler.setFormatter(simple_formatter)
            self.logger.addHandler(console_handler)
        
        # JSON log handler for structured data
        if log_to_file:
            json_log_file = self.log_dir / f"{name}_structured_{timestamp}.jsonl"
            json_handler = JSONLogHandler(json_log_file)
            json_handler.setLevel(logging.INFO)
            self.logger.addHandler(json_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message with optional structured data"""
        if kwargs:
            self.logger.info(f"{message} | Data: {json.dumps(kwargs)}")
        else:
            self.logger.info(message)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional structured data"""
        if kwargs:
            self.logger.debug(f"{message} | Data: {json.dumps(kwargs)}")
        else:
            self.logger.debug(message)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional structured data"""
        if kwargs:
            self.logger.warning(f"{message} | Data: {json.dumps(kwargs)}")
        else:
            self.logger.warning(message)
    
    def error(self, message: str, **kwargs):
        """Log error message with optional structured data"""
        if kwargs:
            self.logger.error(f"{message} | Data: {json.dumps(kwargs)}")
        else:
            self.logger.error(message)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with optional structured data"""
        if kwargs:
            self.logger.critical(f"{message} | Data: {json.dumps(kwargs)}")
        else:
            self.logger.critical(message)
    
    def log_data_collection(self, 
                          platform: str,
                          crisis_id: str,
                          posts_collected: int,
                          start_time: datetime,
                          end_time: datetime,
                          status: str = "success",
                          **additional_data):
        """
        Log data collection activity with structured metadata
        
        Args:
            platform (str): Data source platform (reddit, twitter, etc.)
            crisis_id (str): Crisis event identifier
            posts_collected (int): Number of posts collected
            start_time (datetime): Collection start time
            end_time (datetime): Collection end time
            status (str): Collection status
            **additional_data: Additional structured data
        """
        duration = (end_time - start_time).total_seconds()
        
        log_data = {
            'activity': 'data_collection',
            'platform': platform,
            'crisis_id': crisis_id,
            'posts_collected': posts_collected,
            'duration_seconds': duration,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'status': status,
            'rate_posts_per_second': posts_collected / duration if duration > 0 else 0,
            **additional_data
        }
        
        self.info(f"Data collection completed for {crisis_id} from {platform}", **log_data)
    
    def log_network_analysis(self,
                           crisis_id: str,
                           analysis_type: str,
                           network_metrics: dict,
                           processing_time: float,
                           **additional_data):
        """
        Log network analysis activity
        
        Args:
            crisis_id (str): Crisis event identifier
            analysis_type (str): Type of network analysis
            network_metrics (dict): Network metrics calculated
            processing_time (float): Time taken for analysis in seconds
            **additional_data: Additional structured data
        """
        log_data = {
            'activity': 'network_analysis',
            'crisis_id': crisis_id,
            'analysis_type': analysis_type,
            'processing_time_seconds': processing_time,
            'network_metrics': network_metrics,
            **additional_data
        }
        
        self.info(f"Network analysis completed: {analysis_type} for {crisis_id}", **log_data)
    
    def log_error_with_context(self,
                             error: Exception,
                             context: str,
                             crisis_id: Optional[str] = None,
                             **additional_data):
        """
        Log error with contextual information
        
        Args:
            error (Exception): Exception that occurred
            context (str): Context where error occurred
            crisis_id (str): Crisis event identifier (if applicable)
            **additional_data: Additional structured data
        """
        log_data = {
            'activity': 'error',
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'crisis_id': crisis_id,
            **additional_data
        }
        
        self.error(f"Error in {context}: {error}", **log_data)
    
    def log_performance_metric(self,
                             metric_name: str,
                             metric_value: Union[int, float],
                             unit: str,
                             crisis_id: Optional[str] = None,
                             **additional_data):
        """
        Log performance metrics
        
        Args:
            metric_name (str): Name of the performance metric
            metric_value (Union[int, float]): Value of the metric
            unit (str): Unit of measurement
            crisis_id (str): Crisis event identifier (if applicable)
            **additional_data: Additional structured data
        """
        log_data = {
            'activity': 'performance_metric',
            'metric_name': metric_name,
            'metric_value': metric_value,
            'unit': unit,
            'crisis_id': crisis_id,
            **additional_data
        }
        
        self.info(f"Performance metric - {metric_name}: {metric_value} {unit}", **log_data)

class JSONLogHandler(logging.Handler):
    """Custom handler for structured JSON logging"""
    
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
    
    def emit(self, record):
        """Emit a log record as structured JSON"""
        try:
            log_entry = {
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno,
                'message': record.getMessage(),
            }
            
            # Add any additional structured data from the log message
            if hasattr(record, 'structured_data'):
                log_entry.update(record.structured_data)
            
            with open(self.filename, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception:
            self.handleError(record)

def setup_project_logger(module_name: str, 
                        log_level: str = "INFO") -> CrisisLogger:
    """
    Set up a logger for a project module
    
    Args:
        module_name (str): Name of the module
        log_level (str): Logging level
        
    Returns:
        CrisisLogger: Configured logger instance
    """
    return CrisisLogger(
        name=module_name,
        log_level=log_level,
        log_to_file=True,
        log_to_console=True
    )

# Convenience function for quick logger setup
def get_logger(name: str, level: str = "INFO") -> CrisisLogger:
    """
    Get a logger instance with standard configuration
    
    Args:
        name (str): Logger name
        level (str): Log level
        
    Returns:
        CrisisLogger: Configured logger
    """
    return setup_project_logger(name, level)
