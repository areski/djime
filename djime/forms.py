from datetime import datetime, timedelta

from django import forms
from django.db import models
from django.utils.translation import ugettext as _
from djime.models import Slip, TimeSlice
from project.models import Project


class SlipForm(forms.ModelForm):

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