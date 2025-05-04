"""
Configuration settings for the SCC Criminal Cases RAG system.
"""
import os
from pathlib import Path

# Explicitly import dependencies by their absolute paths
from backend.src.utils.file_utils import ensure_dir_exists
from backend.src.utils.date_utils import generate_date_range_urls

# Base directories - use pathlib for more robust path handling
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
SRC_DIR = Path(__file__).parent.absolute()
DATA_DIR = PROJECT_ROOT / "data"

# SCC scraping configuration
BASE_URL = "https://decisions.scc-csc.ca"
OUTPUT_DIR = DATA_DIR  # Direct output to data directory
TARGET_CASES = 500    # Legacy parameter, kept for backward compatibility
MAX_NO_CHANGE_SCROLLS = 3  # Stop scrolling after this many consecutive scrolls with no new cases
SCROLL_ATTEMPTS = 30  # Number of scroll attempts

# Chrome Driver configuration
CHROME_DRIVER_PATH = os.path.join(SRC_DIR, "chromedriver")

# Other settings
TIMEOUT = 10     # Selenium wait timeout (seconds)
HEADLESS = True  # Whether to use headless mode

# Generate search URLs based on date ranges
SEARCH_URLS = generate_date_range_urls(BASE_URL, subject_id="16")

# Log file paths
LOGS_DIR = SRC_DIR / "logs"
SCRAPER_LOG_FILE = LOGS_DIR / "scraper.log"
MAIN_LOG_FILE = LOGS_DIR / "main.log"
PROCESSOR_LOG_FILE = LOGS_DIR / "processor.log"
EMBEDDINGS_LOG_FILE = LOGS_DIR / "embeddings.log"
RAG_LOG_FILE = LOGS_DIR / "rag.log"
API_LOG_FILE = LOGS_DIR / "api.log"

# Data storage paths
VECTORS_DIR = DATA_DIR / "vectors"
PROCESSED_DIR = DATA_DIR / "processed"
SCRAPED_LINKS_FILE = PROCESSED_DIR / "scraped_links.json"

# RAG settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = "text-embedding-3-large"  # OpenAI embedding model name
EMBEDDING_DIMENSIONS = 3072  # Dimensions for the embedding model
SIMILARITY_TOP_K = 5  # Number of chunks to retrieve for each query

# Ensure directories exist
ensure_dir_exists(LOGS_DIR)
ensure_dir_exists(OUTPUT_DIR)
ensure_dir_exists(PROCESSED_DIR)
ensure_dir_exists(VECTORS_DIR)

# Convert Path objects to strings for compatibility
LOGS_DIR = str(LOGS_DIR)
SCRAPER_LOG_FILE = str(SCRAPER_LOG_FILE)
MAIN_LOG_FILE = str(MAIN_LOG_FILE)
PROCESSOR_LOG_FILE = str(PROCESSOR_LOG_FILE)
EMBEDDINGS_LOG_FILE = str(EMBEDDINGS_LOG_FILE)
RAG_LOG_FILE = str(RAG_LOG_FILE)
API_LOG_FILE = str(API_LOG_FILE)
OUTPUT_DIR = str(OUTPUT_DIR)
VECTORS_DIR = str(VECTORS_DIR)
PROCESSED_DIR = str(PROCESSED_DIR)
SCRAPED_LINKS_FILE = str(SCRAPED_LINKS_FILE)
