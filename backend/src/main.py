"""
Main entry point for the SCC Criminal Cases RAG system.
"""
import os
from typing import Dict, List, Any, Optional, Set
from backend.src.data_collection.manager import perform_search
from backend.src.config import (
    BASE_URL, OUTPUT_DIR, SEARCH_URLS, 
    MAIN_LOG_FILE
)
from backend.src.utils.log_utils import setup_logging

# Set up logging
logger = setup_logging(MAIN_LOG_FILE)

def main() -> int:
    """
    Main entry point for the SCC case scraper.
    
    This function orchestrates the workflow:
    1. Loops through each search URL
    2. Scrapes and downloads case files for each URL
    
    The function handles multiple date ranges and implements an incremental
    approach that only processes new cases not previously scraped.
    
    Returns:
        Total number of cases processed
    """
    logger.info("Starting the scraping process with resume capability...")

    # Execute searches for each URL
    total_processed = 0
    for url in SEARCH_URLS:
        logger.info(f"Processing search URL: {url}")
        processed_count = perform_search(url, OUTPUT_DIR, BASE_URL)
        total_processed += processed_count
        logger.info(f"Completed processing URL: {url}")
        logger.info(f"Total cases processed so far: {total_processed}")

    logger.info(f"All URLs processed. Total cases processed: {total_processed}")
    
    return total_processed

if __name__ == "__main__":
    # Call the main function when the script is executed directly
    cases_processed = main()
    logger.info(f"Script completed. Processed {cases_processed} cases in total.")
