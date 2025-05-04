"""
Module for cleaning and normalizing case text data.
"""
import re
from typing import Dict, Any, List, Optional, Union
import unicodedata
import logging
from bs4 import BeautifulSoup

from backend.src.config import PROCESSOR_LOG_FILE
from backend.src.utils.log_utils import setup_logging

# Set up logging
logger = setup_logging(PROCESSOR_LOG_FILE)

def remove_html_tags(text: str) -> str:
    """
    Remove HTML tags from text.
    
    Args:
        text: HTML text to clean
        
    Returns:
        Cleaned text without HTML tags
    """
    try:
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text(separator=" ", strip=True)
    except Exception as e:
        logger.error(f"Error removing HTML tags: {e}")
        # Fallback to regex if BeautifulSoup fails
        return re.sub(r'<[^>]+>', ' ', text)

def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace by replacing multiple spaces, tabs, and newlines with a single space.
    
    Args:
        text: Text to normalize
        
    Returns:
        Text with normalized whitespace
    """
    return re.sub(r'\s+', ' ', text).strip()

def normalize_unicode(text: str) -> str:
    """
    Normalize Unicode characters to their canonical form.
    
    Args:
        text: Text with potentially non-standard Unicode characters
        
    Returns:
        Text with normalized Unicode characters
    """
    return unicodedata.normalize('NFKC', text)

def normalize_quotes(text: str) -> str:
    """
    Normalize various quote types to standard quotes.
    
    Args:
        text: Text with potentially non-standard quotes
        
    Returns:
        Text with normalized quotes
    """
    # Replace various opening quotes with standard double quote
    text = re.sub(r'[\u201C\u201D\u201E\u201F\u2033\u2036\u275D\u275E\u301D\u301E]', '"', text)
    # Replace various closing quotes with standard double quote
    text = re.sub(r'[\u2018\u2019\u201A\u201B\u2032\u2035\u275B\u275C]', "'", text)
    return text

def remove_citations(text: str) -> str:
    """
    Remove legal citations patterns from text.
    
    Args:
        text: Text with legal citations
        
    Returns:
        Text with citations removed or simplified
    """
    # Remove patterns like "(R. v. Smith, [2022] 1 S.C.R. 123)"
    text = re.sub(r'\([^)]*\[[0-9]{4}\][^)]*\)', '', text)
    # Remove patterns like "(para. 12)"
    text = re.sub(r'\(para\.\s+\d+\)', '', text)
    return text

def clean_text(text: str) -> str:
    """
    Apply a sequence of cleaning operations to text.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
        
    # Apply cleaning steps in sequence
    text = remove_html_tags(text)
    text = normalize_unicode(text)
    text = normalize_quotes(text)
    text = remove_citations(text)
    text = normalize_whitespace(text)
    
    return text

def clean_case_data(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean all text fields in a case data dictionary.
    
    Args:
        case_data: Dictionary containing case data
        
    Returns:
        Dictionary with cleaned text fields
    """
    if not case_data:
        return {}
        
    # Create a deep copy to avoid modifying the original
    cleaned_data = case_data.copy()
    
    # Clean facts text
    if 'facts' in cleaned_data:
        cleaned_data['facts'] = clean_text(cleaned_data['facts'])
    
    # Clean statutes cited
    if 'statutes_cited' in cleaned_data and isinstance(cleaned_data['statutes_cited'], list):
        cleaned_data['statutes_cited'] = [clean_text(statute) for statute in cleaned_data['statutes_cited']]
    
    # Clean metadata fields
    if 'metadata' in cleaned_data and isinstance(cleaned_data['metadata'], dict):
        for key, value in cleaned_data['metadata'].items():
            if isinstance(value, str):
                cleaned_data['metadata'][key] = clean_text(value)
    
    return cleaned_data 