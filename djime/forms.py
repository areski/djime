from datetime import datetime, timedelta

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

        model.descrition = self.cleaned_data['description']