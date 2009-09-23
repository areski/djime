import datetime

from django.db import models, IntegrityError
from django.db.models.signals import pre_save
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

from djime.util import delta_to_seconds, format_seconds
from tasks.models import Task

class TimeSlice(models.Model):
    """
    The TimeSlice records an amount of time spent on a task.

    The starting time is stored and the duration in seconds.
    If the duration is NULL, the slice is assumed to be active - that the
    timer has been started and not stopped yet.

    """
    task = models.ForeignKey(Task, related_name="timeslices", verbose_name=_('task'))
    user = models.ForeignKey(User, related_name="timeslices", verbose_name=_('user'))
    begin = models.DateTimeField(default=datetime.datetime.utcnow, verbose_name=_('start time and date'))
    duration = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('duration in seconds'))
    note = models.TextField(null=True, blank=True, verbose_name=_('note/explanation'))

    def __unicode__(self):
        return _('From %(begin)s') % {'begin': self.begin}

    def calculate_duration(self, end=None, force=False):
        """
        Calculate the duration of the time slice.

        Normally used when ending the slice, this method will not perform
        any changes if the slice already has a duration set, unless the
        force parameter is True.

        Keyword arguments:
        end -- datetime object for the end (default datetime.datetime.utcnow())
        force -- force the duration to be recalculated (default False)

        """
        if not end:
            end = datetime.datetime.utcnow()
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

def timesheet_timeslice_handler(timeslices):
    if not timeslices:
        return timeslices
    timeslices = timeslices.order_by('task', 'note')
    result = []
    test = []
    # create a timeslice that is different from the first timeslice.
    # TODO: why does TimeSlice().task give strange error?
    temp_slice = timeslices[0]
    if not temp_slice.note:
        temp_slice.note = 'a'
    else:
        temp_slice.note += 'a'
    for timeslice in timeslices:
        if timeslice.note == temp_slice.note and timeslice.task == temp_slice.task:
            temp_slice.duration += timeslice.duration
        else:
            result.append(temp_slice)
            temp_slice = timeslice
    result.append(temp_slice)
    return result[1:]