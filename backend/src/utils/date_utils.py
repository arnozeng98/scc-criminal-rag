"""
Date and time utility functions.
"""
import datetime
from typing import List

def generate_date_range_urls(base_url: str, subject_id: str = "16") -> List[str]:
    """
    Generate search URLs based on date ranges spanning 10 years each.
    
    This function creates a series of URLs for searching legal cases, divided into
    10-year periods from 1985 to the current date. It helps handle pagination
    limitations on the website.
    
    Args:
        base_url: Base URL for the search (e.g., "https://decisions.scc-csc.ca")
        subject_id: Subject ID for filtering cases (default: "16" for Criminal cases)
        
    Returns:
        List of generated URLs covering different time periods
    
    Example:
        >>> urls = generate_date_range_urls("https://decisions.scc-csc.ca")
        >>> print(f"Generated {len(urls)} search URLs")
    """
    # Get current date
    today = datetime.datetime.now()
    current_year = today.year
    current_month = today.month
    current_day = today.day
    
    # Create the base search URL template
    base_search_url = f"{base_url}/scc-csc/en/d/s/index.do?cont=&ref=&d1={{d1}}&d2={{d2}}&p=&su={subject_id}&or="
    
    # Generate time ranges
    urls = []
    
    # URL for cases before 1986
    urls.append(
        base_search_url.format(d1="", d2="1985-12-31")
    )
    
    # Generate URLs for 10-year spans dynamically, starting from 1986
    start_year = 1986
    while start_year <= current_year:
        # Calculate end year (10-year span)
        end_year = start_year + 9
        
        # If this range includes the current year, adjust the end date to today
        if current_year <= end_year:
            end_date = f"{current_year}-{current_month:02d}-{current_day:02d}"
        else:
            end_date = f"{end_year}-12-31"
            
        url = base_search_url.format(
            d1=f"{start_year}-01-01",
            d2=end_date
        )
        urls.append(url)
        
        # If we've included the current year, stop adding ranges
        if current_year <= end_year:
            break
        
        # Move to next 10-year span
        start_year += 10
    
    return urls 