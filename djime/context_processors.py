"""
Django context processors used within Djime.
"""
from django.conf import settings
from djime.models import TimeSlice

def statusbar(request):
    """
    Provide a Djime statusbar.

    Displays the running timer, the current task, total time today, etc.
    """
    templatevars = {}
    if request.user.is_authenticated():
        current_slice = TimeSlice.objects.filter(duration=None,
                                                        user=request.user)[:1]
        if current_slice:
            # Unpack the QuerySet to get the model object.
            cslice = current_slice[0]
            slice_time = {
                'year': cslice.begin.year,
                'month': cslice.begin.month-1,
                'day': cslice.begin.day,
                'hour': cslice.begin.hour,
                'minute': cslice.begin.minute,
                'second': cslice.begin.second
            }
            templatevars['djime'] = {
                'slice': cslice,
                'time': slice_time,
                'class': 'timer-running',
                'total_time': cslice.task.display_time()
            }
    return templatevars

