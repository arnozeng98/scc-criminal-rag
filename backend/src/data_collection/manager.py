"""
Manager module for coordinating scraping operations and tracking scraped cases.
"""
from typing import Dict, List, Any, Optional, Set, Tuple
import time
import os
from concurrent.futures import ThreadPoolExecutor
import logging

from backend.src.config import (
    OUTPUT_DIR, SCRAPED_LINKS_FILE, BASE_URL, SEARCH_URLS
)
from backend.src.utils.log_utils import setup_logging
from backend.src.utils.file_utils import load_json_file, save_json_file, ensure_dir_exists

# Lazy import scraper to avoid circular imports
# from .scraper import scrape_cases, download_case

def load_scraped_links(links_file: Optional[str] = None) -> Dict[str, str]:
    """
    Load previously scraped links from storage file.
    
    Retrieves the dictionary of previously scraped links where keys are
    the case URLs and values are the corresponding case numbers.
    
    Args:
        links_file: Optional custom path to the scraped links file
                   (defaults to SCRAPED_LINKS_FILE from config)
    
    Returns:
        Dictionary mapping case URLs to case numbers
    
    Example:
        >>> links = load_scraped_links()
        >>> print(f"Found {len(links)} previously scraped links")
    """
    file_path = links_file if links_file else SCRAPED_LINKS_FILE
    return load_json_file(file_path, default={})

def save_scraped_link(link: str, case_number: str, links_file: Optional[str] = None) -> None:
    """
    Save a newly scraped link with its case number to persistent storage.
    
    Updates the scraped links dictionary with a new entry and saves it
    to the configured storage file.
    
    Args:
        link: URL of the case
        case_number: Case number extracted from the case page
        links_file: Optional custom path to the scraped links file
                   (defaults to SCRAPED_LINKS_FILE from config)
    
    Example:
        >>> save_scraped_link("https://example.com/case/123", "ABC-123")
    """
    file_path = links_file if links_file else SCRAPED_LINKS_FILE
    links = load_scraped_links(file_path)
    links[link] = case_number
    save_json_file(file_path, links)

def save_cases(case_data: List[Dict[str, str]], output_dir: str = OUTPUT_DIR, links_file: Optional[str] = None) -> int:
    """
    Download and save multiple cases in parallel.
    
    For each case in the list, downloads the HTML content and saves it to a file.
    Updates the scraped links file with the case numbers of successfully downloaded cases.
    
    Args:
        case_data: List of dictionaries, each containing title and link for a case
        output_dir: Directory to save downloaded case files
        links_file: Optional custom path to the scraped links file
        
    Returns:
        Number of cases successfully downloaded
        
    Example:
        >>> cases = [{"title": "Case 1", "link": "https://example.com/case/1"}, ...]
        >>> downloaded = save_cases(cases, "./data/raw")
        >>> print(f"Successfully downloaded {downloaded} cases")
    """
    # To avoid circular imports, import scraper here
    from .scraper import download_case
    
    # Get logger from scraper module to ensure consistent logging
    logger = logging.getLogger(SCRAPED_LINKS_FILE)
    
    if not case_data:
        logger.info("No new cases to download")
        return 0
    
    ensure_dir_exists(output_dir)
    logger.info(f"Starting download of {len(case_data)} cases")
    
    successful_downloads = 0
    
    # Define a worker function to handle individual downloads
    def download_worker(case_info: Dict[str, str]) -> Optional[Tuple[str, str]]:
        title = case_info["title"]
        link = case_info["link"]
        
        logger.info(f"Downloading case: {title}")
        success, case_number, _ = download_case(link, output_dir)
        
        if success and case_number:
            logger.info(f"Successfully downloaded case: {title} ({case_number})")
            return link, case_number
        else:
            logger.error(f"Failed to download case: {title}")
            return None
    
    # Use ThreadPoolExecutor to download cases in parallel
    results = []
    with ThreadPoolExecutor(max_workers=4) as executor:  # Limit to 4 parallel downloads
        for case_info in case_data:
            # Add small delay between submitting tasks to avoid overwhelming the server
            time.sleep(0.5)
            future = executor.submit(download_worker, case_info)
            results.append(future)
    
    # Process results and update scraped links
    for future in results:
        result = future.result()
        if result:
            link, case_number = result
            save_scraped_link(link, case_number, links_file)
            successful_downloads += 1
    
    logger.info(f"Download completed. Successfully downloaded {successful_downloads}/{len(case_data)} cases")
    return successful_downloads

def perform_search(url: str, output_dir: str, base_url: str, max_cases: Optional[int] = None, links_file: Optional[str] = None) -> int:
    """
    Execute a complete search and download operation for a single URL.
    
    This is the main orchestration function that:
    1. Scrapes a search URL to find case links
    2. Downloads the cases that haven't been processed yet
    3. Updates the scraped links registry
    
    Args:
        url: Search URL to process
        output_dir: Directory to save downloaded cases
        base_url: Base URL for handling relative links
        max_cases: Maximum number of cases to download (None for unlimited)
        links_file: Optional custom path to the scraped links file
        
    Returns:
        Number of cases successfully processed
        
    Example:
        >>> processed = perform_search("https://decisions.scc-csc.ca/...", "./data/raw", "https://decisions.scc-csc.ca")
        >>> print(f"Processed {processed} cases")
    """
    # To avoid circular imports, import scraper here
    from .scraper import scrape_cases
    
    # Get logger from scraper module to ensure consistent logging
    logger = logging.getLogger(SCRAPED_LINKS_FILE)
    
    logger.info(f"Processing search URL: {url}")
    
    # Scrape case links from the search page
    cases = scrape_cases(url)
    
    # Limit the number of cases if max_cases is specified
    if max_cases is not None:
        original_count = len(cases)
        cases = cases[:max_cases]
        logger.info(f"Limited to {len(cases)}/{original_count} cases due to max_cases setting")
    
    # Download the cases
    processed_count = save_cases(cases, output_dir, links_file)
    
    logger.info(f"Search URL processing completed. Processed {processed_count} cases")
    return processed_count 