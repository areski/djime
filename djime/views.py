from datetime import date

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from djime.models import TimeSlice
from djime.forms import TimeSliceSheetForm
from tasks.models import Task
from projects.models import Project

try:
    import json
except ImportError:
    from django.utils import simplejson as json

def my_tasks(request, group_slug=None, template_name="djime/my_tasks.html", bridge=None):
    task_list = request.user.assigned_tasks.all()

    return render_to_response(template_name, {
        'task_list': task_list,
    }, context_instance=RequestContext(request))

def timesheet(request, group_slug=None, template_name="djime/timesheet.html", bridge=None):
    if request.method == 'GET':
        form = TimeSliceSheetForm(request.user)
    elif request.method == 'POST':
        form = TimeSliceSheetForm(request.user, request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            timeslice = TimeSlice(
                task=cd['task'],
                user=request.user,
                duration=cd['duration'],
                note=cd['note']
            )
            timeslice.save()
    today = date.today()
    return render_to_response(template_name, {
        'slice_list': TimeSlice.objects.select_related().filter(
                            user=request.user, begin__day=today.day,
                            begin__month=today.month, begin__year=today.year),
        'timesheet_timeslice_form': form
    }, context_instance=RequestContext(request))

def project_json(request, project_id):
    tasks = Task.objects.filter(object_id=project_id).order_by('summary')
    json = ''
    for task in tasks:
         json += '<option value="%(id)s">%(summary)s</option>' % {
                                            'id': task.id, 'summary': task.summary}
    return HttpResponse(json)
