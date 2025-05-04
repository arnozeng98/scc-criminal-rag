"""
Web scraper for collecting SCC case data.
"""
import os
import time
from typing import Dict, List, Any, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Import from restructured modules
from backend.src.config import (
    BASE_URL, OUTPUT_DIR, SCROLL_ATTEMPTS, MAX_NO_CHANGE_SCROLLS,
    TIMEOUT, HEADLESS, SCRAPER_LOG_FILE
)
from backend.src.utils.log_utils import setup_logging
from backend.src.utils.file_utils import load_json_file, save_json_file, sanitize_filename
from .manager import load_scraped_links, save_scraped_link

# Set up logging
logger = setup_logging(SCRAPER_LOG_FILE)

def setup_driver() -> webdriver.Chrome:
    """
    Initialize and configure Selenium WebDriver with necessary options.
    
    Sets up Chrome WebDriver with appropriate settings for scraping,
    including headless mode if enabled in configuration.
    
    Returns:
        Configured Chrome WebDriver instance
    
    Example:
        >>> driver = setup_driver()
        >>> driver.get("https://example.com")
        >>> driver.quit()
    """
    service = Service(ChromeDriverManager().install())
    options = Options()
    if HEADLESS:
        options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")  # Fix DevTools log issues
    options.add_argument("--log-level=3")  # Reduce the log level and reduce console output
    return webdriver.Chrome(service=service, options=options)

def scrape_cases(search_url: str, stop_after_first: bool = False) -> List[Dict[str, str]]:
    """
    Scrape case links from a search results page.
    
    Handles scrolling through the search results page to load all available
    case links via lazy loading. Stops when no new cases appear after multiple
    scrolls or when maximum scroll attempts is reached.
    
    Args:
        search_url: URL of the search results page
        stop_after_first: If True, stops after finding the first unprocessed case
                         (useful for testing to avoid loading all links)
        
    Returns:
        List of dictionaries containing case information (title, link)
        
    Example:
        >>> cases = scrape_cases("https://decisions.scc-csc.ca/scc-csc/en/d/s/index.do?...")
        >>> print(f"Found {len(cases)} new cases to scrape")
        >>> # For testing, get just one link quickly
        >>> test_case = scrape_cases(url, stop_after_first=True)
    """
    driver = setup_driver()
    driver.get(search_url)
    time.sleep(3)  # Allow the page to load

    # Load previously scraped links to check against
    scraped_links = load_scraped_links()
    logger.info(f"Loaded {len(scraped_links)} previously scraped links for reference")

    # Track consecutive scrolls with no new content
    last_count = 0
    no_change_count = 0
    total_scrolls = 0
    
    case_data = []
    
    # Continue scrolling until we detect no change in MAX_NO_CHANGE_SCROLLS consecutive scrolls
    # or we reach the maximum scroll attempts as a safety limit
    while no_change_count < MAX_NO_CHANGE_SCROLLS and total_scrolls < SCROLL_ATTEMPTS:
        # If we're in testing mode and already found a case, stop scrolling
        if stop_after_first and len(case_data) > 0:
            logger.info(f"Stop after first enabled: Found {len(case_data)} unprocessed case, stopping scroll")
            break
            
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        total_scrolls += 1
        
        try:
            search_iframe = WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "decisia-iframe"))
            )
            driver.switch_to.frame(search_iframe)
            cases = driver.find_elements(By.CSS_SELECTOR, "div.metadata")
            current_count = len(cases)
            
            # If we're in testing mode, check for unprocessed cases right away
            if stop_after_first:
                # Check each case and add first unprocessed one to the list
                for case in cases:
                    try:
                        a_elem = case.find_element(By.CSS_SELECTOR, "span.title a")
                        title = a_elem.text.strip()
                        href = a_elem.get_attribute("href")
                        full_link = BASE_URL + href if href.startswith("/") else href
                        
                        # Check if the link has already been scraped
                        if full_link not in scraped_links:
                            case_data.append({"title": title, "link": full_link})
                            logger.info(f"Found unprocessed case for testing: {title}")
                            break  # Stop after finding the first case
                    except Exception as e:
                        logger.error(f"Error extracting case link: {e}")
                        continue
            
            driver.switch_to.default_content()
            
            logger.info(f"Scroll #{total_scrolls}: Found {current_count} cases (previous: {last_count})")
            
            if current_count == last_count:
                no_change_count += 1
                logger.info(f"No new cases found after scroll. Consecutive no-change scrolls: {no_change_count}/{MAX_NO_CHANGE_SCROLLS}")
            else:
                no_change_count = 0  # Reset the counter when we find new cases
                last_count = current_count
                
            # If we're in testing mode and found a case, stop scrolling
            if stop_after_first and len(case_data) > 0:
                break
                
        except Exception as e:
            logger.error(f"Error during scrolling: {e}")
            break
    
    # If we're in testing mode and already have a case, skip the final extraction
    if stop_after_first and len(case_data) > 0:
        driver.quit()
        logger.info(f"Test mode: Using first unprocessed case found during scrolling")
        return case_data
    
    reason = "Maximum scroll attempts reached" if total_scrolls >= SCROLL_ATTEMPTS else "No new cases found after consecutive scrolls"
    if stop_after_first and len(case_data) > 0:
        reason = "Found first unprocessed case for testing"
    logger.info(f"Stopped scrolling: {reason}. Total scrolls: {total_scrolls}, Total cases found: {last_count}")

    # If we get here, we need to do a full extraction (non-testing case or no case found yet)
    case_data = []
    try:
        search_iframe = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "decisia-iframe"))
        )
        driver.switch_to.frame(search_iframe)
        cases = driver.find_elements(By.CSS_SELECTOR, "div.metadata")
        
        logger.info(f"Extracting details from {len(cases)} cases...")
        
        for case in cases:
            try:
                # Extract title and link
                a_elem = case.find_element(By.CSS_SELECTOR, "span.title a")
                title = a_elem.text.strip()
                href = a_elem.get_attribute("href")
                
                # Handle relative URLs
                full_link = BASE_URL + href if href.startswith("/") else href
                
                # Check if the link has already been scraped
                if full_link not in scraped_links:
                    case_data.append({"title": title, "link": full_link})
                    logger.debug(f"Added new case: {title}")
                else:
                    logger.debug(f"Skipping already scraped case: {title}")
            except Exception as e:
                logger.error(f"Error extracting case details: {e}")
                continue
                
        logger.info(f"Found {len(case_data)} new cases to scrape")
        
    except Exception as e:
        logger.error(f"Error during case extraction: {e}")
    
    driver.quit()
    return case_data

def download_case(url: str, output_dir: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Download and save the HTML content of a single case.
    
    Retrieves the case page, extracts its case number (or uses title as a fallback),
    and saves the HTML to a file.
    
    Args:
        url: URL of the case to download
        output_dir: Directory to save the downloaded case HTML
        
    Returns:
        Tuple containing:
            - Success status (bool)
            - Case number or identifier (str or None if not found)
            - Path where the file was saved (str or None if failed)
            
    Example:
        >>> success, case_id, saved_path = download_case("https://example.com/case/123", "./data/raw")
        >>> if success:
        >>>     print(f"Saved case {case_id} to {saved_path}")
    """
    driver = setup_driver()
    success = False
    case_number = None
    saved_path = None
    
    try:
        driver.get(url)
        time.sleep(2)  # Allow page to load
        
        # Try to extract case number from the page
        try:
            case_number_elem = driver.find_element(By.XPATH, "//td[text()='Case number']/following-sibling::td")
            case_number = case_number_elem.text.strip()
            logger.info(f"Found case number: {case_number}")
        except Exception as e:
            logger.warning(f"Could not extract case number: {e}")
            
            # Fallback: Use title element if available
            try:
                title_elem = driver.find_element(By.CSS_SELECTOR, "h3.title")
                title = title_elem.text.strip()
                case_number = f"title-{sanitize_filename(title)}"
                logger.info(f"Using title as identifier: {case_number}")
            except Exception as title_e:
                logger.warning(f"Could not extract title: {title_e}")
                
                # Last resort: Use URL timestamp as a unique identifier
                timestamp = int(time.time())
                case_number = f"citation-{timestamp}"
                logger.info(f"Using timestamp as identifier: {case_number}")
        
        # Get the HTML content
        html_content = driver.page_source
        
        # Save the content to a file
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{sanitize_filename(case_number)}.html"
        file_path = os.path.join(output_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Saved case to {file_path}")
        success = True
        saved_path = file_path
        
    except Exception as e:
        logger.error(f"Error downloading case {url}: {e}")
    
    finally:
        driver.quit()
        
    return success, case_number, saved_path 