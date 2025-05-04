#!/usr/bin/env python
"""
Script to run the case data processing pipeline.

This script extracts structured data from raw case HTML files,
cleans the text, and splits it into chunks for embedding.
"""
import sys
import os
import argparse
from typing import List, Dict, Any, Optional
import logging
import time

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
project_root = os.path.dirname(backend_dir)
sys.path.insert(0, project_root)

from backend.src.processor.extractor import extract_all_cases, extract_case_chunks, process_all_cases
from backend.src.config import (
    OUTPUT_DIR, PROCESSED_DIR, PROCESSOR_LOG_FILE
)
from backend.src.utils.log_utils import setup_logging

# Set up logging
logger = setup_logging(PROCESSOR_LOG_FILE)

def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(description="Process SCC case data")
    parser.add_argument(
        "--input-dir", 
        type=str, 
        default=OUTPUT_DIR, 
        help=f"Directory containing raw HTML files (default: {OUTPUT_DIR})"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default=PROCESSED_DIR, 
        help=f"Directory to save processed data (default: {PROCESSED_DIR})"
    )
    
    return parser.parse_args()

def main() -> int:
    """
    Main entry point for the processor script.
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    args = parse_args()
    
    logger.info("Starting the case data processing pipeline...")
    logger.info(f"Input directory: {args.input_dir}")
    logger.info(f"Output directory: {args.output_dir}")
    
    start_time = time.time()
    
    try:
        # Extract and process all cases
        processed_cases = extract_all_cases(args.input_dir, args.output_dir)
        logger.info(f"Processed {len(processed_cases)} cases")
        
        # Extract chunks from the processed cases
        case_chunks = extract_case_chunks(processed_cases, args.output_dir)
        logger.info(f"Extracted {len(case_chunks)} chunks")
        
        elapsed_time = time.time() - start_time
        logger.info(f"Processing completed in {elapsed_time:.2f} seconds")
        
        return 0
        
    except Exception as e:
        logger.exception(f"Error during processing: {e}")
        return 1

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