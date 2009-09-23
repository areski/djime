from django import template
from django.utils.translation import ugettext_lazy as _

from djime.util import format_seconds

register = template.Library()

def slice_time_display(value):
    """
    Convert a timeslice's duration in seconds to something more
    presentable like 1:30 for 1 hour and 30 minutes instead of 5400
    seconds
    """
    return format_seconds(value)

def total_time(slices):
    """
    Takes a QuerySet of TimeSlices and calculates their total time.
    """
    total = 0
    # @@@ Use aggregation when we can use Django 1.1.
    for slice in slices.values('duration'):
        total += slice['duration']
    return total

register.filter('slice_time_display', slice_time_display)
register.filter('total_time', total_time)

