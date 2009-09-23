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


def timesheet_timeslice_handler(timeslices):
    if not timeslices:
        return timeslices
    timeslices = timeslices.order_by('task', 'note')
    result = []
    test = []
    # Create a timeslice like object, that is unique.
    temp_slice =  type('temp_slice', (object,), {'note': 0, 'task':0})
    for timeslice in timeslices:
        if timeslice.note == temp_slice.note and timeslice.task == temp_slice.task:
            temp_slice.duration += timeslice.duration
        else:
            result.append(temp_slice)
            temp_slice = timeslice
    result.append(temp_slice)
    return result[1:]
