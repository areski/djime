import datetime
from django.db import models, IntegrityError
from django.contrib.auth.models import User
from project.models import Project, Client
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import pre_save
from djime.signals import timeslice_save
from djime.util import delta_to_seconds, format_seconds


class Slip(models.Model):
    """
    The slip is a task, assignment or similar that time is registered on.

    The slip is the personal work slip, ie. it registers how much time a
    particular person has spent on a task. This can be related to projects
    and clients.

    """
    name = models.CharField(max_length=128, verbose_name=_('name'))
    user = models.ForeignKey(User, related_name="slips", blank=True, null=True, verbose_name=_('user'))
    project = models.ForeignKey(Project, blank=True, null=True, verbose_name=_('project'))
    client = models.ForeignKey(Client, blank=True, null=True, verbose_name=_('client'))
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('updated'))

    def __unicode__(self):
        return self.name

    def display_time(self):
        """ Display the amount of time on this slip. """
        seconds = 0
        for slice in self.timeslice_set.all():
            seconds += slice.duration

        return format_seconds(seconds)


    def display_days_time(self, date):
        """ Display the amount of time on this slip for a specific day. """
        seconds = 0
        for slice in self.timeslice_set.filter(begin__range=(date, date+datetime.timedelta(days=1))):
            seconds += slice.duration
        return seconds

    def is_active(self):
        """ Simple filter to determine whether this slip is active. """
        slice = self.timeslice_set.filter(duration=None)
        return bool(slice)


class TimeSlice(models.Model):
    """
    The TimeSlice records an amount of time spent on a slip.

    The starting time is stored and the duration in seconds.
    If the duration is NULL, the slice is assumed to be active - that the
    timer has been started and not stopped yet.

    """
    begin = models.DateTimeField(default=datetime.datetime.now, verbose_name=_('start time and date'))
    duration = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('duration in seconds'))
    slip = models.ForeignKey(Slip, verbose_name=_('slip'))
    user = models.ForeignKey(User, related_name="timeslices", blank=True, null=True, verbose_name=_('user'))
    note = models.TextField(null=True, blank=True, verbose_name=_('note/explanation'))

    def __unicode__(self):
        return _('From %(begin)s') % {'begin': self.begin}

    def calculate_duration(self, end=datetime.datetime.now(), force=False):
        """
        Calculate the duration of the time slice.

        Normally used when ending the slice, this method will not perform
        any changes if the slice already has a duration set, unless the
        force parameter is True.

        Keyword arguments:
        end -- datetime object for the end (default datetime.datetime.now())
        force -- force the duration to be recalculated (default False)

        """
        if self.duration is None or force is True:
            self.duration = delta_to_seconds(end - self.begin)

class DataImport(models.Model):
    """
    The DataImport model is used when importing data into Djime.

    It serves as storage and some sort of permanent record of the changes
    made by an import of data from another system.

    """
    user = models.ForeignKey(User, verbose_name=_('user'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created'))
    completed = models.DateTimeField(blank=True, null=True, verbose_name=_('completed'))
    complete_data = models.FileField(upload_to='import_data/complete/%Y/%m/', verbose_name=_('complete data'))
    partial_data = models.FileField(upload_to='import_data/partial/%Y/%m/', verbose_name=_('partial data'))

# Add database triggers for extra processing.
pre_save.connect(timeslice_save, sender=TimeSlice)

