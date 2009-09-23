from datetime import datetime, timedelta
from exceptions import ValueError

from django import forms
from django.db import models
from django.utils.translation import ugettext as _

from djime.models import TimeSlice
from tasks.models import Task
from projects.models import Project

class TimeSliceSheetForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
            super(TimeSliceSheetForm, self).__init__(*args, **kwargs)
            project_choices = []
            for project in Project.objects.select_related().filter(members=user).order_by('name'):
                project_choices.append((project.id, project.name))
            self.fields['project'].choices = project_choices

    duration = forms.CharField(required=True)
    note = forms.CharField(required=False)
    project = forms.ChoiceField(required=False)
    task = forms.CharField(required=False, widget=forms.Select)

    def clean_task(self):
        try:
            task = Task.objects.get(pk=int(self.cleaned_data['task']))
        except Task.DoesNotExist, ValueError:
            # This should never happen unless some one hacks the code.
            raise forms.ValidationError(_('An unexpected error happened, please contact the system administration if the problem persists.'))
        return task

    def clean_duration(self):
        duration_list = self.cleaned_data['duration'].split(':')
        if len(duration_list) > 2:
            raise forms.ValidationError(_('You cannot enter time with two colons (:).'))
        try:
            hour = int(duration_list[0])
            if len(duration_list) > 1:
                minute = int(duration_list[1])
            else:
                minute = 0
        except ValueError:
            raise forms.ValidationError(_('You must enter duration formatted as a number: "2" or "1:15".'))
        return (hour * 60 + minute) * 60