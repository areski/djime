import new
import inspect
from datetime import date

from tasks.models import Task
from djime.util import format_seconds

# MetaClass and MetaObject is taken form the django-granular-permissions app.
# This enables us to inject methods on any given model.
class MetaClass(type):
    def __new__(self, classname, classbases, classdict):
        try:
            frame = inspect.currentframe()
            frame = frame.f_back
            if frame.f_locals.has_key(classname):
                old_class = frame.f_locals.get(classname)
                for name,func in classdict.items():
                    if inspect.isfunction(func):
                        setattr(old_class, name, func)
                return old_class
            return type.__new__(self, classname, classbases, classdict)
        finally:
            del frame

class MetaObject(object):
    __metaclass__ = MetaClass

class Task(MetaObject):
    def is_active(self):
        """ Simple filter to determine whether this task is active. """
        tslice = self.timeslices.filter(duration=None)
        return bool(tslice)

    def display_time(self):
        """ Display the amount of time on this task. """
        seconds = 0
        for tslice in self.timeslices.all():
            if tslice.duration:
                seconds += tslice.duration

        return format_seconds(seconds)

    def display_user_time(self, user):
        """ Display the amount of time on this task for selected user. """
        seconds = 0
        for tslice in self.timeslices.filter(user=user):
            if tslice.duration:
                seconds += tslice.duration
        return format_seconds(seconds)
