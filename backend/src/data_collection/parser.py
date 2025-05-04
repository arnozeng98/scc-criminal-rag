"""
Parser module for extracting structured information from SCC case HTML files.
"""
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup
import re
import os
import logging

from backend.src.config import SCRAPER_LOG_FILE
from backend.src.utils.log_utils import setup_logging

# Set up logging
logger = setup_logging(SCRAPER_LOG_FILE)

def extract_case_metadata(html_content: str) -> Dict[str, Any]:
    """
    Extract metadata from a case HTML page.
    
    Parses the HTML content of a case page and extracts structured metadata
    including title, case number, date, judges, and other fields.
    
    Args:
        html_content: HTML content of the case page
        
    Returns:
        Dictionary containing the extracted metadata
        
    Example:
        >>> with open("case_12345.html", "r", encoding="utf-8") as f:
        >>>     html = f.read()
        >>> metadata = extract_case_metadata(html)
        >>> print(f"Case title: {metadata.get('title')}")
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    metadata = {}
    
    # Extract basic metadata
    try:
        metadata['title'] = soup.find('h3', class_='title').text.strip() if soup.find('h3', class_='title') else None
    except Exception as e:
        logger.error(f"Error extracting title: {e}")
        metadata['title'] = None
    
    # Extract table-based metadata
    metadata_fields = [
        ('collection', 'Collection'),
        ('date', 'Date'),
        ('neutral_citation', 'Neutral citation'),
        ('case_number', 'Case number'),
        ('judges', 'Judges'),
        ('on_appeal_from', 'On appeal from'),
        ('subjects', 'Subjects')
    ]
    
    for field_name, label in metadata_fields:
        try:
            element = soup.find('td', text=label)
            if element:
                value = element.find_next_sibling('td').text.strip()
                metadata[field_name] = value
            else:
                metadata[field_name] = None
        except Exception as e:
            logger.error(f"Error extracting {field_name}: {e}")
            metadata[field_name] = None
    
    return metadata

def extract_facts_section(html_content: str) -> str:
    """
    Extract the 'Facts' section from a case HTML document.
    
    Locates the 'Facts' section in the document by finding an underlined
    header containing the word 'facts', then extracts all content until
    the next underlined header.
    
    Args:
        html_content: HTML content of the case page
        
    Returns:
        String containing the extracted facts or an empty string if not found
        
    Example:
        >>> with open("case_12345.html", "r", encoding="utf-8") as f:
        >>>     html = f.read()
        >>> facts = extract_facts_section(html)
        >>> print(f"Extracted {len(facts)} characters of facts")
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    facts_content = []
    found_facts = False
    
    elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    for element in elements:
        if found_facts:
            # Check for the next underlying section to stop
            if element.find('u'):
                break
            facts_content.append(element.get_text(strip=True))
        elif element.find('u') and 'facts' in element.get_text(strip=True).lower():
            found_facts = True
    
    return ' '.join(facts_content)

def extract_statutes_cited(html_content: str, filter_regex: Optional[str] = None) -> List[str]:
    """
    Extract statutes and regulations cited in a case.
    
    Finds the 'Statutes and Regulations Cited' section in the document,
    and extracts all paragraphs. Optionally filters by a regex pattern.
    
    Args:
        html_content: HTML content of the case page
        filter_regex: Optional regex pattern to filter statutes (e.g. "Criminal|Penal")
        
    Returns:
        List of strings, each representing a statute
        
    Example:
        >>> with open("case_12345.html", "r", encoding="utf-8") as f:
        >>>     html = f.read()
        >>> statutes = extract_statutes_cited(html, "Criminal")
        >>> for statute in statutes:
        >>>     print(f"Found statute: {statute}")
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    content = []
    
    # Compile regex if provided
    regex = re.compile(filter_regex, re.IGNORECASE) if filter_regex else None
    
    statutes_start = soup.find('b', text='Statutes and Regulations Cited')
    if statutes_start:
        current = statutes_start.find_next('p')
        while current and current.find('b') is None:
            if 'Authors Cited' in current.text:
                break
            text = current.text.strip()
            if text:
                # Apply filter if regex is provided
                if not regex or regex.search(text):
                    content.append(text)
            current = current.find_next('p')
    
    return content

def parse_case_file(file_path: str) -> Dict[str, Any]:
    """
    Parse an HTML case file and extract structured information.
    
    Reads an HTML file from disk and extracts metadata, facts, and
    statutes cited.
    
    Args:
        file_path: Path to the HTML case file
        
    Returns:
        Dictionary containing the extracted information
        
    Example:
        >>> case_data = parse_case_file("./data/cases/12345.html")
        >>> print(f"Case title: {case_data['metadata']['title']}")
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        # Extract information
        metadata = extract_case_metadata(html_content)
        facts = extract_facts_section(html_content)
        statutes = extract_statutes_cited(html_content)
        
        # Check if it's a criminal case
        is_criminal = False
        if metadata.get('subjects') and 'Criminal' in metadata['subjects']:
            is_criminal = True
        
        # Create the result dictionary
        result = {
            'metadata': metadata,
            'facts': facts,
            'statutes_cited': statutes,
            'is_criminal': is_criminal,
            'file_path': file_path
        }
        
        return result
    
    except Exception as e:
        logger.error(f"Error parsing case file {file_path}: {e}")
        return {
            'metadata': {},
            'facts': '',
            'statutes_cited': [],
            'is_criminal': False,
            'file_path': file_path,
            'error': str(e)
        } 