"""
File utility functions.
"""
import os
import json
import logging
import re
from typing import Any, Optional

def ensure_dir_exists(directory: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    This is a convenience function that creates all necessary parent
    directories if they don't exist yet.
    
    Args:
        directory: Directory path to check/create
    
    Example:
        >>> ensure_dir_exists("data/output/results")
        # Creates all directories in the path if they don't exist
    """
    os.makedirs(directory, exist_ok=True)

def load_json_file(file_path: str, default: Any = None) -> Any:
    """
    Load data from a JSON file with error handling.
    
    Safely loads JSON data from a file. If the file doesn't exist or
    if there's an error during loading, returns the default value.
    
    Args:
        file_path: Path to the JSON file to load
        default: Default value to return if file doesn't exist or load fails
        
    Returns:
        Loaded data from JSON file or default value if loading fails
    
    Example:
        >>> data = load_json_file("settings.json", default={"version": "1.0"})
    """
    if default is None:
        default = {}
        
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading JSON file {file_path}: {e}")
            return default
    return default

def save_json_file(file_path: str, data: Any, indent: int = 2) -> bool:
    """
    Save data to a JSON file with error handling.
    
    Safely saves data to a JSON file with proper encoding and formatting.
    Creates all necessary directories in the path if they don't exist.
    
    Args:
        file_path: Path where to save the JSON file
        data: Data to save (must be JSON serializable)
        indent: JSON indentation level for pretty-printing
        
    Returns:
        True if saving was successful, False otherwise
    
    Example:
        >>> success = save_json_file("results.json", {"status": "completed", "count": 42})
    """
    try:
        ensure_dir_exists(os.path.dirname(file_path))
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        return True
    except Exception as e:
        logging.error(f"Error saving JSON file {file_path}: {e}")
        return False

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a string to be used as a valid filename across operating systems.
    
    Replaces characters that are problematic in filenames with safe alternatives.
    This ensures that filenames will be valid on Windows, macOS and Linux.
    Spaces are removed to create more compact filenames.
    
    Args:
        filename: Original filename or string
        
    Returns:
        Sanitized filename safe to use on all operating systems
    
    Example:
        >>> safe_name = sanitize_filename("case/report: 2022?")
        >>> print(safe_name)  # Outputs: "case-report-2022_"
        >>> safe_name = sanitize_filename("18190, 18292")
        >>> print(safe_name)  # Outputs: "18190-18292"
    """
    # Handle leading/trailing whitespace
    filename = filename.strip()
    
    # 1. Replace path separators and OS-specific characters
    os_chars_map = {
        '/': '-',
        '\\': '-',
        ':': '-',
        '*': '_',
        '?': '_',
        '|': '_',
        '<': '_',
        '>': '_',
        '"': "'",
        ',': '-'  # Handle multiple case numbers
    }
    
    for char, replacement in os_chars_map.items():
        filename = filename.replace(char, replacement)
    
    # 2. Replace other potentially problematic characters
    other_chars = r'[%&{}\$!@#\^=+]'
    filename = re.sub(other_chars, '_', filename)
    
    # 3. Remove all spaces (Option 3)
    filename = filename.replace(' ', '')
    
    # Ensure the filename isn't empty and doesn't have problematic starts/ends
    if not filename or filename.isspace():
        filename = "unnamed_file"
    
    # Remove any duplicate special characters
    filename = re.sub(r'[-_]{2,}', '-', filename)
    
    return filename 