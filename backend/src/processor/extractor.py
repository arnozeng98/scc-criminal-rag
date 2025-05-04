"""
Module for extracting and organizing structured data from raw case files.
"""
import os
import glob
from typing import List, Dict, Any, Optional, Set, Tuple
import logging
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from backend.src.config import (
    OUTPUT_DIR, PROCESSED_DIR, PROCESSOR_LOG_FILE, PROJECT_ROOT
)
from backend.src.utils.log_utils import setup_logging
from backend.src.utils.file_utils import save_json_file, ensure_dir_exists
from backend.src.data_collection.parser import parse_case_file
from .cleaner import clean_case_data
from .chunker import create_case_chunks

# Set up logging
logger = setup_logging(PROCESSOR_LOG_FILE)

def get_relative_path(file_path: str) -> str:
    """
    Convert an absolute path to a path relative to the project root.
    
    Args:
        file_path: Absolute file path
        
    Returns:
        Path relative to the project root
    """
    try:
        # Convert paths to Path objects for easier manipulation
        abs_path = Path(file_path).resolve()
        project_root = Path(PROJECT_ROOT).resolve()
        
        # Get the relative path
        rel_path = abs_path.relative_to(project_root)
        
        # Convert back to string with forward slashes
        return str(rel_path).replace('\\', '/')
    except ValueError:
        # If path is not relative to project root, return original
        logger.warning(f"Could not convert {file_path} to relative path")
        return file_path

def process_case_file(file_path: str) -> Dict[str, Any]:
    """
    Process a single case file by parsing, cleaning, and chunking.
    
    Args:
        file_path: Path to the case HTML file
        
    Returns:
        Dictionary containing the processed case data
    """
    try:
        # Parse the case file
        logger.info(f"Parsing case file: {file_path}")
        case_data = parse_case_file(file_path)
        
        # Check if it's a criminal case
        if not case_data.get('is_criminal', False):
            logger.info(f"Skipping non-criminal case: {file_path}")
            return {}
        
        # Clean the case data
        cleaned_data = clean_case_data(case_data)
        
        # Generate chunks for the case
        chunks = create_case_chunks(cleaned_data)
        
        # Convert absolute path to relative path
        relative_path = get_relative_path(file_path)
        
        # Create the processed result
        result = {
            'metadata': cleaned_data.get('metadata', {}),
            'facts': cleaned_data.get('facts', ''),
            'statutes_cited': cleaned_data.get('statutes_cited', []),
            'is_criminal': cleaned_data.get('is_criminal', False),
            'file_path': relative_path,
            'chunks': chunks
        }
        
        logger.info(f"Successfully processed case: {file_path}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing case file {file_path}: {e}")
        
        # Convert absolute path to relative path even for error cases
        relative_path = get_relative_path(file_path)
        
        return {
            'metadata': {},
            'facts': '',
            'statutes_cited': [],
            'is_criminal': False,
            'file_path': relative_path,
            'chunks': [],
            'error': str(e)
        }

def extract_all_cases(input_dir: str = OUTPUT_DIR, output_dir: str = PROCESSED_DIR) -> List[Dict[str, Any]]:
    """
    Extract and process all case files in the input directory.
    
    Args:
        input_dir: Directory containing raw case HTML files
        output_dir: Directory to save processed case data
        
    Returns:
        List of dictionaries containing processed case data
    """
    ensure_dir_exists(output_dir)
    
    # Find all HTML files in the input directory
    html_files = glob.glob(os.path.join(input_dir, '*.html'))
    logger.info(f"Found {len(html_files)} HTML files to process")
    
    if not html_files:
        logger.warning(f"No HTML files found in {input_dir}")
        return []
    
    # Process files in parallel
    processed_cases = []
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        results = executor.map(process_case_file, html_files)
        
        for result in results:
            if result and result.get('is_criminal', False):
                processed_cases.append(result)
    
    logger.info(f"Processed {len(processed_cases)} criminal cases")
    
    # Save the processed cases to a JSON file
    output_file = os.path.join(output_dir, "processed_cases.json")
    save_json_file(output_file, processed_cases)
    logger.info(f"Saved processed cases to {output_file}")
    
    return processed_cases

def extract_case_chunks(processed_cases: List[Dict[str, Any]], output_dir: str = PROCESSED_DIR) -> List[Dict[str, Any]]:
    """
    Extract all chunks from processed cases and save them to a file.
    
    Args:
        processed_cases: List of processed case dictionaries
        output_dir: Directory to save the chunks data
        
    Returns:
        List of dictionaries containing case chunks
    """
    all_chunks = []
    
    for case in processed_cases:
        if 'chunks' in case and case['chunks']:
            all_chunks.extend(case['chunks'])
    
    logger.info(f"Extracted {len(all_chunks)} total chunks from {len(processed_cases)} cases")
    
    # Save the chunks to a JSON file
    output_file = os.path.join(output_dir, "case_chunks.json")
    save_json_file(output_file, all_chunks)
    logger.info(f"Saved case chunks to {output_file}")
    
    return all_chunks

def process_all_cases() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Process all case files and extract chunks.
    
    This is the main entry point for the extraction process.
    
    Returns:
        Tuple containing:
            - List of processed cases
            - List of case chunks
    """
    # Extract and process all cases
    processed_cases = extract_all_cases()
    
    # Extract chunks from the processed cases
    case_chunks = extract_case_chunks(processed_cases)
    
    return processed_cases, case_chunks 