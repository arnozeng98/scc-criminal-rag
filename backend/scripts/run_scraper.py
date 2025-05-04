#!/usr/bin/env python
"""
Script to run the SCC case scraper.

This script provides a command-line interface to run the scraper
with various options for controlling its behavior.
"""
import sys
import os
import argparse
from typing import List, Optional
import logging

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
project_root = os.path.dirname(backend_dir)
sys.path.insert(0, project_root)

from backend.src.data_collection.manager import perform_search
from backend.src.config import (
    BASE_URL, OUTPUT_DIR, SEARCH_URLS, MAIN_LOG_FILE
)
from backend.src.utils.log_utils import setup_logging

# Set up logging
logger = setup_logging(MAIN_LOG_FILE)

def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(description="Run the SCC case scraper")
    parser.add_argument(
        "--max-cases", 
        type=int, 
        default=None, 
        help="Maximum number of cases to download per URL (default: no limit)"
    )
    parser.add_argument(
        "--url-index", 
        type=int, 
        default=None, 
        help="Index of the URL to process (default: process all URLs)"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default=OUTPUT_DIR, 
        help=f"Directory to save downloaded cases (default: {OUTPUT_DIR})"
    )
    
    return parser.parse_args()

def main() -> int:
    """
    Main entry point for the scraper script.
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    args = parse_args()
    
    logger.info("Starting the scraping process...")
    logger.info(f"Output directory: {args.output_dir}")
    
    if args.max_cases:
        logger.info(f"Maximum cases per URL: {args.max_cases}")
    
    # Determine which URLs to process
    urls_to_process: List[str] = []
    if args.url_index is not None:
        if 0 <= args.url_index < len(SEARCH_URLS):
            urls_to_process = [SEARCH_URLS[args.url_index]]
            logger.info(f"Processing single URL at index {args.url_index}")
        else:
            logger.error(f"Invalid URL index: {args.url_index}, must be between 0 and {len(SEARCH_URLS)-1}")
            return 1
    else:
        urls_to_process = SEARCH_URLS
        logger.info(f"Processing all {len(urls_to_process)} URLs")
    
    # Execute searches for each URL
    total_processed = 0
    for i, url in enumerate(urls_to_process):
        logger.info(f"Processing URL {i+1}/{len(urls_to_process)}: {url}")
        processed_count = perform_search(url, args.output_dir, BASE_URL, args.max_cases)
        total_processed += processed_count
        logger.info(f"Completed processing URL. Cases processed: {processed_count}")
        logger.info(f"Total cases processed so far: {total_processed}")

    logger.info(f"All URLs processed. Total cases processed: {total_processed}")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Unhandled exception: {e}")
        sys.exit(1) 