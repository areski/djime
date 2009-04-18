import datetime
from django.db import models, IntegrityError
from django.contrib.auth.models import User
from project.models import Project, Client
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import pre_save
from djime.signals import timeslice_save
from djime.util import delta_to_seconds, format_seconds


class Slip(models.Model):
    name = models.CharField(max_length=128, verbose_name=_('name'))
    user = models.ForeignKey(User, related_name="slips", blank=True, null=True, verbose_name=_('user'))
<<<<<<< HEAD:djime/models.py
    project = models.ForeignKey(Project, blank=True, null=True, verbose_name=_('project'))
    client = models.ForeignKey(Client, blank=True, null=True, verbose_name=_('client'))
    description = models.TextField(blank=True)
=======
    project = models.ForeignKey(Project, blank = True, null=True, verbose_name=_('project'))
    client = models.ForeignKey(Client, blank = True, null=True, verbose_name=_('client'))
    description = models.TextField(blank=True)
    #type = models.CharField(max_length=32)
    due = models.DateField(null=True, blank=True, verbose_name=_('due'))
>>>>>>> adi/master:djime/models.py
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('updated'))

    def __unicode__(self):
        return self.name

    def display_time(self):
        seconds = 0
        for slice in self.timeslice_set.all():
            seconds += slice.duration

        return format_seconds(seconds)


    def display_days_time(self, date):
        seconds = 0
        for slice in self.timeslice_set.filter(begin__year=date.year, begin__month=date.month, begin__day=date.day):
            seconds += slice.duration
        return seconds

    def is_active(self):
        slice = self.timeslice_set.filter(duration = None)
        return bool(slice)


class TimeSlice(models.Model):
    begin = models.DateTimeField(default=datetime.datetime.now, verbose_name=_('start time and date'))
    duration = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('duration in seconds'))
    slip = models.ForeignKey(Slip, verbose_name=_('slip'))
    user = models.ForeignKey(User, related_name="timeslices", blank=True, null=True, verbose_name=_('user'))
<<<<<<< HEAD:djime/models.py
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
=======
    description = models.TextField(blank=True)
    duration = models.PositiveIntegerField(editable=False, default=0, verbose_name=_('duration'))

    def __unicode__(self):
        if self.end:
            return _('From %(begin)s to %(end)s') % {'begin': self.begin.strftime('%Y-%m-%d %H:%M:%S'), 'end': self.end.strftime('%Y-%m-%d %H:%M:%S')}
        else:
            return _('From %(begin)s') % {'begin': self.begin.strftime('%Y-%m-%d %H:%m:%S')}
>>>>>>> adi/master:djime/models.py

class DataImport(models.Model):
    user = models.ForeignKey(User, verbose_name=_('user'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created'))
    completed = models.DateTimeField(blank=True, null=True, verbose_name=_('completed'))
    complete_data = models.FileField(upload_to='import_data/complete/%Y/%m/', verbose_name=_('complete data'))
    partial_data = models.FileField(upload_to='import_data/partial/%Y/%m/', verbose_name=_('partial data'))

pre_save.connect(timeslice_save, sender=TimeSlice)

