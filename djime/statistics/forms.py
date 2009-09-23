from django import forms
from datetime import date, timedelta
import re
from exceptions import ValueError

from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from djime.forms import TimeSliceBaseForm
from projects.models import Project
from tasks.models import Task

class BillingSelectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BillingSelectionForm, self).__init__(*args, **kwargs)
        project_choices = [('0', _('All Projects'))]
        task_choices = [('0', _('All Tasks'))]
        user_choices = [('0', _('All Users'))]
        for project in Project.objects.all().order_by('name'):
            project_choices.append((project.id, project.name))
        self.fields['project'].choices = project_choices
        if project_choices:
            tasks = Task.objects.filter(object_id=project_choices[0][0])
            for task in tasks:
                task_choices.append((task.id, task.summary))
        self.fields['task'].choices = task_choices
        for user in User.objects.all().order_by('username'):
            user_choices.append((user.id, user.username))
        self.fields['user'].choices = user_choices

    project = forms.ChoiceField(required=True)
    task = forms.ChoiceField(required=True)
    user = forms.ChoiceField(required=True)
    begin = forms.CharField(required=False)
    end = forms.CharField(required=False)

    def clean_project(self):
        """
        Cleaning/validation method for the project field
        """
        if self.cleaned_data.has_key('project'):
            cd_project = self.cleaned_data['project']
            if int(cd_project) == 0:
                return 'all'
            else:
                project = Project.objects.filter(pk=cd_project)
                if project:
                    return project[0].id
                else:
                    raise forms.ValidationError(_('Selected project is not a valid'))

    def clean_task(self):
        """
        Cleaning/validation method for the task field
        """
        if self.cleaned_data.has_key('task'):
            cd_task = self.cleaned_data['task']
            if int(cd_task) == 0:
                return 'all'
            else:
                tasks = Task.objects.filter(pk=cd_task)
                if tasks:
                    return tasks[0].id
                else:
                    raise forms.ValidationError(_('Selected task is not a valid'))

    def clean_user(self):
        """
        Cleaning/validation method for the user field
        """
        if self.cleaned_data.has_key('user'):
            cd_user = self.cleaned_data['user']
            if int(cd_user) == 0:
                return 'all'
            else:
                users = User.objects.filter(pk=cd_user)
                if users:
                    return users[0].id
                else:
                    raise forms.ValidationError(_('Selected user is not a valid'))

    def clean_begin(self):
        start_date = self.cleaned_data.get("begin", '')
        if start_date:
            if start_date and not re.match("[0-9]{4}[-]{1}[0-9]{2}[-]{1}[0-9]{2}$", start_date):
                raise forms.ValidationError(_("Begin date has invalid format, must be 'yyyy-mm-dd'"))
            start = start_date.split('-')
            try:
                s_date = date(int(start[0]),int(start[1]),int(start[2]))
            except ValueError:
                raise forms.ValidationError(_("Begin date does not exist"))
            return start_date
        return 0

    def clean_end(self): 
        end_date = self.cleaned_data.get("end", '')
        if end_date:
            if end_date and not re.match("[0-9]{4}[-]{1}[0-9]{2}[-]{1}[0-9]{2}$", end_date):
                raise forms.ValidationError(_("End date has invalid format, must be 'yyyy-mm-dd'"))
            end = end_date.split('-')
            try:
                e_date = date(int(end[0]),int(end[1]),int(end[2]))
                return end_date
            except ValueError:
                raise forms.ValidationError(_("End date does not exist"))
        return 0
        
    def clean(self):
        cleaned_data = self.cleaned_data
        start_date = cleaned_data.get("begin", None)
        end_date = cleaned_data.get("end", None)
        if start_date and end_date:
            start = start_date.split('-')
            s_date = date(int(start[0]),int(start[1]),int(start[2]))
            end = end_date.split('-')
            e_date = date(int(end[0]),int(end[1]),int(end[2]))
            if (e_date - s_date) < timedelta(days=0):
                raise forms.ValidationError(_("Begin date must be before end date"))
        return cleaned_data

class DateSelectionForm(forms.Form):
    date = forms.CharField()

    def clean(self):
        cleaned_data = self.cleaned_data
        date_data = cleaned_data.get("date")
        # first check that the user has entered 2 values seperated by space
        # something space.
        date_list = date_data.split()
        if len(date_list) != 3:
            raise forms.ValidationError(_("You have to enter 2 dates, in the date field, seperated by SPACE and a DASH (-) and a SPACE. Hint, use the date picker provided"))
        # start and end dates are set from the date list.
        start_date = date_list[0]
        end_date = date_list[-1]
        # use regular expression to check if the user has entered the date in
        # the format 'yyyy-mm-dd'
        if not re.match("[0-9]{4}[-]{1}[0-9]{2}[-]{1}[0-9]{2}$", start_date):
            raise forms.ValidationError(_("Start date has invalid format, must be 'yyyy-mm-dd'"))

        if not re.match("[0-9]{4}[-]{1}[0-9]{2}[-]{1}[0-9]{2}$", end_date):
            raise forms.ValidationError(_("Start date has invalid format, must be 'yyyy-mm-dd'"))

        # since re test passed, the dates can now be splitted by the
        # dash to create a list with the year, month and day.
        start = start_date.split('-')
        end = end_date.split('-')

        # using try and catching ValueError to check if the user has
        # entered an invalid date like Feb 31 or Jan 55 ect.
        try:
            s_date = datetime.date(int(start[0]),int(start[1]),int(start[2]))
        except ValueError:
            raise forms.ValidationError(_("Start date does not exist"))
        try:
            e_date = datetime.date(int(end[0]),int(end[1]),int(end[2]))
        except ValueError:
            raise forms.ValidationError(_("End date does not exist"))

        # Lastly we check to see that the two dates are between 1 and
        # 60 days apart, and that the begin date is before the end date
        if e_date - (s_date) > datetime.timedelta(days=60):
            raise forms.ValidationError(_("Difference between end and start date must be lower than 60 days"))
        if e_date - (s_date) < datetime.timedelta(days=1):
            raise forms.ValidationError(_("End date must be after start date"))

        cleaned_data['start'] = s_date
        cleaned_data['end'] = e_date
        # Always returning the cleaned data.
        return cleaned_data