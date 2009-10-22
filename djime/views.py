# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _

from djime.models import TimeSlice
from djime.util import timesheet_timeslice_handler
from djime.forms import TimeSliceSheetForm, TimesheetWeekForm
from djime.forms import TimesheetMonthForm, TimesheetQuarterForm
from djime.forms import TimesheetYearForm, TimesheetDateForm
from djime.forms import TimeSliceBaseForm
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

@login_required
def timesheet(request, method=None, year=None, method_value=0, group_slug=None, template_name="djime/timesheet.html", bridge=None):
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
                note=cd['note'],
            )
            timeslice.save()

    today = date.today()
    if not method:
        headline = 'today'
        timeslices = TimeSlice.objects.select_related().filter(
                            user=request.user, begin__day=today.day,
                            begin__month=today.month, begin__year=today.year)
    elif method == 'week':
        week = int(method_value)
        if year:
            year = int(year)
            headline = 'week %s - %s' % (week, year)
        elif week:
            year = today.year
            headline = 'week %s - %s' % (week, year)
        else:
            headline = 'this week'
            week = today.isocalendar()[1]
            year = today.year

        start_date = date(year, 1, 1) + timedelta(days=(week-2)*7)
        while start_date.isocalendar()[1] != week:
            start_date += timedelta(days=1)
        end_date = start_date + timedelta(days=7)

        timeslices = TimeSlice.objects.select_related().filter(
                                    user=request.user,
                                    begin__range=(start_date, end_date))
    elif method == 'month':
        month = int(method_value)
        if year:
            headline = '%s - %s' % (datetime(2000, month, 1).strftime('%B'), year)
        elif month:
            year = today.year
            headline = '%s - %s' % (datetime(2000, month, 1).strftime('%B'), year)
        else:
            headline = 'this month'
            month = today.month
            year = today.year
        timeslices = TimeSlice.objects.select_related().filter(
                            user=request.user, begin__month=month,
                                                    begin__year=year)
    elif method == 'quarter':
        quarter = int(method_value)
        quarter_suffix = ['1st', '2nd', '3rd', '4th']
        quarter_end = [31, 30, 30, 31]
        if year:
            year = int(year)
            headline = '%s quarter - %s' % (quarter_suffix[quarter-1], year)
        elif quarter:
            year = today.year
            headline = '%s quarter - %s' % (quarter_suffix[quarter-1], year)
        else:
            headline = 'this quarter'
            quarter = (today.month - 1) / 3 + 1
            year = today.year
        start_date = date(year, quarter * 3 - 2, 1)
        end_date = date(year, quarter * 3, quarter_end[quarter-1]) + \
                                                    timedelta(days=1)
        timeslices = TimeSlice.objects.select_related().filter(
                                    user=request.user,
                                    begin__range=(start_date, end_date))
    elif method == 'year':
        year = int(method_value)
        if not year:
            year = today.year
        if year == today.year:
            headline = 'this year'
        else:
            headline = year
        timeslices = TimeSlice.objects.select_related().filter(
                                user=request.user, begin__year=year)


    return render_to_response(template_name, {
        'slice_list': timesheet_timeslice_handler(timeslices),
        'timesheet_timeslice_form': form,
        'headline': headline
    }, context_instance=RequestContext(request))

@login_required
def timesheet_select_form(request, group_slug=None, template_name="djime/select.html", bridge=None):
    timesheet_week_form = TimesheetWeekForm()
    timesheet_month_form = TimesheetMonthForm()
    timesheet_quarter_form = TimesheetQuarterForm()
    timesheet_year_form = TimesheetYearForm()
    timesheet_date_form = TimesheetDateForm()
    variable = 'week'
    if request.method == 'POST':
        if request.POST.has_key('week'):
            form = timesheet_week_form = TimesheetWeekForm(request.POST)
            if form.is_valid():
                return HttpResponseRedirect(reverse('djime_wmq_timesheet',
                            kwargs={'method': 'week',
                                    'method_value': form.cleaned_data['week'],
                                    'year': form.cleaned_data['year']}))
        elif request.POST.has_key('month'):
            form = timesheet_month_form = TimesheetMonthForm(request.POST)
            if form.is_valid():
                return HttpResponseRedirect(reverse('djime_wmq_timesheet',
                            kwargs={'method': 'month',
                                    'method_value': form.cleaned_data['month'],
                                    'year': form.cleaned_data['year']}))
            variable = 'month'
        elif request.POST.has_key('quarter'):
            form = timesheet_quarter_form = TimesheetQuarterForm(request.POST)
            if form.is_valid():
                return HttpResponseRedirect(reverse('djime_wmq_timesheet',
                            kwargs={'method': 'quarter',
                                    'method_value': form.cleaned_data['quarter'],
                                    'year': form.cleaned_data['year']}))
            variable = 'quarter'
        elif request.POST.has_key('year'):
            form = timesheet_year_form = TimesheetYearForm(request.POST)
            if form.is_valid():
                return HttpResponseRedirect(reverse('djime_wmqy_timesheet',
                        kwargs={'method': 'year',
                                'method_value': form.cleaned_data['year']}))
            variable = 'year'
        elif request.POST.has_key('begin'):
            form = timesheet_date_form = TimesheetDateForm(request.POST)
            if form.is_valid():
                return HttpResponseRedirect(reverse('djime_date_timesheet',
                        kwargs={'start_date': form.cleaned_data['begin'],
                                'end_date': form.cleaned_data['end']}))
            variable = 'custom'
    return render_to_response(template_name, {
        'timesheet_week_form': timesheet_week_form,
        'timesheet_month_form': timesheet_month_form,
        'timesheet_quarter_form': timesheet_quarter_form,
        'timesheet_year_form': timesheet_year_form,
        'timesheet_date_form': timesheet_date_form,
        variable: 'checked="checked"',
    }, context_instance=RequestContext(request))

@login_required
def timesheet_date(request, end_date, start_date, group_slug=None, template_name="djime/timesheet.html", bridge=None):
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
                note=cd['note'],
            )
            timeslice.save()

    headline = '%s to %s' % (start_date, end_date)
    s_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    e_date = datetime.strptime(end_date, '%Y-%m-%d').date() + \
                                                    timedelta(days=1)
    timeslices = TimeSlice.objects.select_related().filter(
                                user=request.user,
                                begin__range=(s_date, e_date))

    return render_to_response(template_name, {
        'slice_list': timesheet_timeslice_handler(timeslices),
        'timesheet_timeslice_form': form,
        'headline': headline
    }, context_instance=RequestContext(request))

@login_required()
def timetrack(request, group_slug=None, template_name="djime/timetrack.html", bridge=None):
    if request.method == 'GET':
        form = TimeSliceBaseForm(request.user)
    elif request.method == 'POST':
        post = request.POST
        form = TimeSliceBaseForm(request.user, request.POST)
        if form.is_valid():
            active_slices = TimeSlice.objects.filter(user=request.user,
                                                                duration=None)
            # there should only be at most one active timeslice at any
            # time but incase some error has occured, we want to stop
            # all active timeslices whenever a new one is started.
            for timeslice in active_slices:
                timeslice.calculate_duration()
                timeslice.save()
            cd = form.cleaned_data
            new_slice = TimeSlice(
                task=cd['task'],
                user=request.user,
                note=cd['note'],
            )
            new_slice.save()
            if request.POST.has_key('destination'):
                project = Project.objects.get(pk=cd['project'])
                return HttpResponseRedirect(reverse(request.POST['destination'], kwargs={'group_slug': project.slug }))

    return render_to_response(template_name, {
        'timestrack_timeslice_form': form
    }, context_instance=RequestContext(request))


@login_required()
def task_action(request, task_id, action):
    if request.method not in ('GET', 'POST'):
        return HttpResponseNotAllowed(('POST', 'GET'))

    # make sure the task exists
    task = get_object_or_404(Task, pk=task_id)

    if action == 'start':
        # Make sure the user doesn't already have an active time slice
        # for this Task
        if not TimeSlice.objects.filter(user=request.user,
                                        task=task_id, duration=None):
            if request.POST.has_key('begin'):
                start_time = 0
                time = request.POST['begin']
                if type(time) == unicode:
                    time = time.split(', ')
                    start_time = datetime(int(time[0]), int(time[1]), int(time[2]), int(time[3]), int(time[4]), int(time[5]), int(time[6]))
                else:
                    start_time = datetime.utcnow()
            else:
                start_time = datetime.utcnow()

            # Stop active timeslices if any
            slice_query_set = TimeSlice.objects.filter(user=request.user,
                                                                duration=None)
            if slice_query_set:
                for tslice in slice_query_set:
                    tslice.calculate_duration()
                    tslice.save()

            new_slice = TimeSlice.objects.create(user=request.user, task_id=task_id, begin=start_time)
            new_slice.save()
            return HttpResponse('Your timeslice begin time %(start_time)s has been created' % {'start_time': start_time})
        else:
            return HttpResponse('You already have an unfinished time slice for this task. A new one has not been created.', status=409)

    elif action == 'stop':
        time_slice = get_object_or_404(TimeSlice, user=request.user, task=task_id, duration=None)
        if request.POST.has_key('end'):
            time = request.POST['end']
            if type(time) == unicode:
                time = time.split(', ')
                end_time = datetime(int(time[0]), int(time[1]), int(time[2]), int(time[3]), int(time[4]), int(time[5]), int(time[6]))
        else:
            end_time = datetime.utcnow()
        time_slice.calculate_duration(end_time)
        time_slice.save()
        return HttpResponse('Your timeslice for task "%(summary)s", begintime %(begin)s has been stopped at %(end)s' % {'summary': time_slice.task.summary, 'begin': time_slice.begin, 'end': end_time})

    elif action == 'get_json':
        if task.group:
            project_name = tasl.group.name
        else:
            project_name = ''
        data = {'active': task.is_active(),
                'task_time' : task.display_time(),
                'task_summary' : task.summary,
                'project': project_name}
        return HttpResponse(json.dumps(data))

    else:
        # TODO: Make a return for only action allowed is start/stop ect
        pass

def project_json(request, project_id):
    if int(project_id) == 0:
        tasks = []
    else:
        tasks = Task.objects.filter(object_id=project_id).order_by('summary')
    json = ''
    if request.GET.get('get') == 'all':
        json += '<option value="0">%s</option>' % _('All Tasks')
    for task in tasks:
         json += '<option value="%(id)s">%(summary)s</option>' % {
                                                    'id': task.id,
                                                    'summary': task.summary}
    return HttpResponse(json)

@login_required()
def ajax_user(request, project_id):
    users = User.objects.exclude(project=project_id)
    holder = []
    for user in users:
        holder.append(user.username)
    return HttpResponse(json.dumps(holder))