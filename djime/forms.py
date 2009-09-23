from datetime import datetime, timedelta, date
from exceptions import ValueError
import re

from django import forms
from django.db import models
from django.utils.translation import ugettext as _

from djime.models import TimeSlice
from tasks.models import Task
from projects.models import Project

class TimeSliceBaseForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(TimeSliceBaseForm, self).__init__(*args, **kwargs)
        project_choices = []
        task_choices = []
        for project in Project.objects.filter(member_users=user).order_by(
                                                                    'name'):
            project_choices.append((project.id, project.name))
        self.fields['project'].choices = project_choices
        if project_choices:
            tasks = Task.objects.filter(object_id=project_choices[0][0])
            for task in tasks:
                task_choices.append((task.id, task.summary))
        self.fields['task'].choices = task_choices

    note = forms.CharField(required=False, widget=forms.Textarea)
    project = forms.ChoiceField(required=False)
    task = forms.ChoiceField(required=False)

    def clean_task(self):
        try:
            task = Task.objects.get(pk=int(self.cleaned_data['task']))
        except Task.DoesNotExist, ValueError:
            # This should never happen unless some one hacks the code.
            raise forms.ValidationError(_('An unexpected error happened, \
                                    please contact the system administration \
                                    if the problem persists.'))
        return task

class TimeSliceSheetForm(TimeSliceBaseForm):
    def __init__(self, *args, **kwargs):
        super(TimeSliceSheetForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['duration', 'note', 'project', 'task']

    duration = forms.CharField(required=True)
    def clean_duration(self):
        duration_list = self.cleaned_data['duration'].split(':')
        if len(duration_list) > 2:
            raise forms.ValidationError(_('You cannot enter time with two \
                                                                colons (:).'))
        try:
            hour = int(duration_list[0])
            if len(duration_list) > 1:
                minute = int(duration_list[1])
            else:
                minute = 0
        except ValueError:
            raise forms.ValidationError(_('You must enter duration formatted \
                                                as a number: "2" or "1:15".'))
        return (hour * 60 + minute) * 60

class TimesheetWeekForm(forms.Form):
    week = forms.IntegerField(required=True)
    year = forms.IntegerField(required=True, initial=datetime.today().year)

class TimesheetMonthForm(forms.Form):
    month = forms.IntegerField(required=True)
    year = forms.IntegerField(required=True, initial=datetime.today().year)

class TimesheetQuarterForm(forms.Form):
    quarter = forms.IntegerField(required=True)
    year = forms.IntegerField(required=True, initial=datetime.today().year)

class TimesheetYearForm(forms.Form):
    year = forms.IntegerField(required=True, initial=datetime.today().year)

class TimesheetDateForm(forms.Form):
    begin = forms.CharField(required=True)
    end = forms.CharField(required=True)

    def clean(self):
        cleaned_data = self.cleaned_data
        start_date = cleaned_data.get("begin", '')
        end_date = cleaned_data.get("end", '')
        # use regular expression to check if the user has entered the date in
        # the format 'yyyy-mm-dd'
        if start_date and not re.match("[0-9]{4}[-]{1}[0-9]{2}[-]{1}[0-9]{2}$",
                                                                start_date):
            raise forms.ValidationError(_("Start date has invalid format, \
                                                    must be 'yyyy-mm-dd'"))

        if end_date and not re.match("[0-9]{4}[-]{1}[0-9]{2}[-]{1}[0-9]{2}$",
                                                                    end_date):
            raise forms.ValidationError(_("End date has invalid format, \
                                                    must be 'yyyy-mm-dd'"))

        if not start_date or not end_date:
            return cleaned_data
        # since re test passed, the dates can now be splitted by the
        # dash to create a list with the year, month and day.
        start = start_date.split('-')
        end = end_date.split('-')

        # using try and catching ValueError to check if the user has
        # entered an invalid date like Feb 31 or Jan 55 ect.
        try:
            s_date = date(int(start[0]),int(start[1]),int(start[2]))
        except ValueError:
            raise forms.ValidationError(_("Start date does not exist"))
        try:
            e_date = date(int(end[0]),int(end[1]),int(end[2]))
        except ValueError:
            raise forms.ValidationError(_("End date does not exist"))

        return cleaned_data