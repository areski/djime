"""
Djime utility functions.
"""
from math import floor

def delta_to_seconds(delta):
    """Convert a timedelta object into the equivalent number of seconds."""
    return (delta.days * 86400) + delta.seconds

def format_seconds(seconds):
    """
    Format seconds for display as hours and minutes.

    """
    duration = {
        'hours': floor(seconds / 3600),
        'minutes': floor((seconds % 3600) / 60),
        'seconds': floor(seconds % 60),
    }

    return '%02i:%02i' % (duration['hours'], duration['minutes'])


