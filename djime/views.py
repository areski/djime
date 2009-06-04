from datetime import date

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from djime.models import TimeSlice
from tasks.models import Task

def my_tasks(request, group_slug=None, template_name="djime/my_tasks.html"):
    task_list = request.user.assigned_tasks.all()

    return render_to_response(template_name, {
        'task_list': task_list,
    }, context_instance=RequestContext(request))

def timesheet(request, group_slug=None, template_name="djime/timesheet.html"):
    today = date.today()

    return render_to_response(template_name, {
        'slice_list': TimeSlice.objects.select_related().filter(
                            user=request.user, begin__day=today.day,
                            begin__month=today.month, begin__year=today.year),
    }, context_instance=RequestContext(request))


