from datetime import datetime, timedelta
from exceptions import ValueError

from django import forms
from django.db import models
from django.utils.translation import ugettext as _

from djime.models import Slip, TimeSlice
from project.models import Project


class SlipForm(forms.ModelForm):
    project = forms.CharField(required=False)

    def clean_project(self):
        """
        Cleaning/validation method for the project field
        """
        if self.cleaned_data.has_key('project') and self.cleaned_data['project']:
            project = Project.objects.filter(name__iexact=self.cleaned_data['project'], members=self.data['user'])[:1]
            if project:
                return project[0]
            else:
                raise forms.ValidationError(_('%s is not a valid project.' % self.cleaned_data['project']))
        else:
            # If project field was empty, return None as cleaned data.
            return None

    class Meta:
        model = Slip
        fields = ('name', 'client', 'project')


class TimeSliceForm(forms.Form):
    date = forms.DateField()
    duration   = forms.IntegerField()
    description = forms.CharField(widget=forms.Textarea)

    def update_model(self, model):
        d = datetime.now()
        td = timedelta(hours=self.cleaned_data['duration'])
        # begin is from now - duration since I've done the work already.
        model.begin = datetime.combine(self.cleaned_data['date'], d.time()) - td
        # end is now 
        model.end = datetime.combine(self.cleaned_data['date'], d.time())

        model.description = self.cleaned_data['description']


class TimeSliceSheetForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
            super(TimeSliceSheetForm, self).__init__(*args, **kwargs)
            project_choices = []
            for project in Project.objects.select_related().filter(members=user, state='active').order_by('name'):
                if project.slip_set.filter(user=user):
                    project_choices.append((project.id, project.name))
            self.fields['project'].choices = project_choices

    duration = forms.CharField(required=True)
    note = forms.CharField(required=False)
    project = forms.ChoiceField(required=False)
    slip = forms.CharField(required=False, widget=forms.Select)

    def clean_slip(self):
        try:
            slip = Slip.objects.get(pk=int(self.cleaned_data['slip']))
        except Slip.DoesNotExist, ValueError:
            # This should never happen unless some one hacks the code.
            raise forms.ValidationError(_('An unexpected error happened, please contact the system administration if the problem persists.'))
        return slip

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

