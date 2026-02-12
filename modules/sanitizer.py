"""
Sanitizer Module: Parses relative time expressions into absolute datetime objects.
"""
import dateparser
from datetime import datetime

def parse_relative_time(time_str):
    """
    Converts a relative time string (e.g., "in 20 minutes") to a datetime object.
    Returns None if parsing fails.
    """
    settings = {
        'PREFER_DATES_FROM': 'future',
        'RELATIVE_BASE': datetime.now() # Explicitly set base to now
    }
    
    dt = dateparser.parse(time_str, settings=settings)
    return dt
