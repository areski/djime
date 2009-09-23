"""
Djime utility functions.
"""
from math import floor
import calendar
from datetime import timedelta

try:
    import json
except ImportError:
    from django.utils import simplejson as json

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
    timeslices = timeslices.exclude(duration=None).order_by('task', 'note')
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

def flot_timeslices(timeslices, start, end):
    """
    Function to convert a Queryset of timselices into data that can be
    used by flot in json format.
    """
    timeslices.exclude(duration=None)
    min_val = calendar.timegm(start.timetuple()) * 1000
    vdict = {}
    while start <= end:
        vdict[start] = 0
        start += timedelta(days=1)
    for tslice in timeslices:
        vdict[tslice.begin.date()] += tslice.duration
    vlist = []
    keys = vdict.keys()
    keys.sort()
    for key in keys[:-1]:
        # Only show entries where the days duration is above 10 mins.
        if vdict[key] > 600:
            vlist.append([calendar.timegm(key.timetuple()) * 1000,
                                                        vdict[key] * 1000])
    result = json.dumps({
        'flot': vlist,
        'min': min_val,
        'max': calendar.timegm((end - timedelta(days=1)).timetuple()) * 1000,
    })
    return result
