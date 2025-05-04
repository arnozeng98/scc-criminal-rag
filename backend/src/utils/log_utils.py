"""
Logging utility functions.
"""
import os
import sys
import logging
import codecs
from typing import Optional

from .file_utils import ensure_dir_exists

def setup_logging(log_file: str, log_level: int = logging.INFO) -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        log_file: Path to the log file
        log_level: Logging level (default: INFO)
        
    Returns:
        Logger instance configured with file and console handlers
    """
    # Make sure the directory exists
    log_dir = os.path.dirname(log_file)
    ensure_dir_exists(log_dir)
    
    # Create a custom logger
    logger = logging.getLogger(log_file)
    logger.setLevel(log_level)
    
    # Clear any existing handlers
    if logger.handlers:
        logger.handlers = []
    
    # Create handlers
    # File handler - using utf-8 encoding to handle special characters
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(log_level)
    
    # Console handler - using utf-8 encoding to handle special characters
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setStream(codecs.getwriter('utf-8')(sys.stdout.buffer) if hasattr(sys.stdout, 'buffer') else sys.stdout)
    
    # Create formatters and add it to handlers
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    file_formatter = logging.Formatter(log_format)
    console_formatter = logging.Formatter(log_format)
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger 