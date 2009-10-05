import calendar
from datetime import timedelta, date, datetime

from django.contrib.auth.decorators import login_required
from django.http import *
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.core.urlresolvers import reverse

from djime.forms import TimesheetWeekForm
from djime.forms import TimesheetMonthForm, TimesheetQuarterForm
from djime.forms import TimesheetYearForm, TimesheetDateForm
from djime.models import TimeSlice
from djime.util import timesheet_timeslice_handler, flot_timeslices
from djime.statistics.forms import BillingSelectionForm

@login_required()
def index(request, group_slug=None, template_name="djime/statistics/index.html", bridge=None):
    start = date.today()
    end = date.today()
    while start.isocalendar()[1] == end.isocalendar()[1]:
           start -= timedelta(days=1)
    start += timedelta(days=1)
    end = start + timedelta(days=7)
    timeslices = TimeSlice.objects.filter(user=request.user,
                                                    begin__range=(start, end))
    return render_to_response(template_name, {
                    'flot_data': flot_timeslices(timeslices, start, end),
                    'headline': _('this week')},
                              context_instance=RequestContext(request))

@login_required()
def statistics(request, method=None, year=None, method_value=0, group_slug=None, template_name="djime/statistics/index.html", bridge=None, ajax=False):
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
            week = method_value = today.isocalendar()[1]
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
            year = int(year)
            headline = '%s - %s' % (datetime(2000, month, 1).strftime('%B'), year)
        elif month:
            year = today.year
            headline = '%s - %s' % (datetime(2000, month, 1).strftime('%B'), year)
        else:
            headline = 'this month'
            month = method_value = today.month
            year = today.year
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month+1, 1)
        timeslices = TimeSlice.objects.select_related().filter(
                    user=request.user, begin__range=(start_date, end_date))
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
            quarter = method_value = (today.month - 1) / 3 + 1
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
            year = method_value = today.year
        if year == today.year:
            headline = 'this year'
        else:
            headline = year
        start_date = date(year, 1, 1)
        end_date = date(year + 1, 1, 1)
        timeslices = TimeSlice.objects.select_related().filter(
                                user=request.user, begin__year=year)

    if ajax:
        return flot_timeslices(timeslices, start_date, end_date)
    return render_to_response(template_name, {
                'flot_data': flot_timeslices(timeslices, start_date, end_date),
                'headline': headline,
                'method': method,
                'method_value': method_value,},
                            context_instance=RequestContext(request))

@login_required
def statistics_select_form(request, group_slug=None, template_name="djime/statistics/select.html", bridge=None):
    statistics_week_form = TimesheetWeekForm()
    statistics_month_form = TimesheetMonthForm()
    statistics_quarter_form = TimesheetQuarterForm()
    statistics_year_form = TimesheetYearForm()
    statistics_date_form = TimesheetDateForm()
    variable = 'week'
    if request.method == 'POST':
        if request.POST.has_key('week'):
            form = statistics_week_form = TimesheetWeekForm(request.POST)
            if form.is_valid():
                return HttpResponseRedirect(reverse('djime_wmq_statistics',
                            kwargs={'method': 'week',
                                    'method_value': form.cleaned_data['week'],
                                    'year': form.cleaned_data['year']}))
        elif request.POST.has_key('month'):
            form = statistics_month_form = TimesheetMonthForm(request.POST)
            if form.is_valid():
                return HttpResponseRedirect(reverse('djime_wmq_statistics',
                        kwargs={'method': 'month',
                                'method_value': form.cleaned_data['month'],
                                'year': form.cleaned_data['year']}))
            variable = 'month'
        elif request.POST.has_key('quarter'):
            form = statistics_quarter_form = TimesheetQuarterForm(request.POST)
            if form.is_valid():
                return HttpResponseRedirect(reverse('djime_wmq_statistics',
                        kwargs={'method': 'quarter',
                                'method_value': form.cleaned_data['quarter'],
                                'year': form.cleaned_data['year']}))
            variable = 'quarter'
        elif request.POST.has_key('year'):
            form = statistics_year_form = TimesheetYearForm(request.POST)
            if form.is_valid():
                return HttpResponseRedirect(reverse('djime_wmqy_statistics',
                        kwargs={'method': 'year',
                                'method_value': form.cleaned_data['year']}))
            variable = 'year'
        elif request.POST.has_key('begin'):
            form = statistics_date_form = TimesheetDateForm(request.POST)
            if form.is_valid():
                return HttpResponseRedirect(reverse('djime_date_statistics',
                        kwargs={'start_date': form.cleaned_data['begin'],
                                'end_date': form.cleaned_data['end']}))
            variable = 'custom'
    return render_to_response(template_name, {
        'statistics_week_form': statistics_week_form,
        'statistics_month_form': statistics_month_form,
        'statistics_quarter_form': statistics_quarter_form,
        'statistics_year_form': statistics_year_form,
        'statistics_date_form': statistics_date_form,
        variable: 'checked="checked"',
    }, context_instance=RequestContext(request))

@login_required
def statistics_date(request, end_date, start_date, group_slug=None, template_name="djime/statistics/index.html", bridge=None):
    headline = '%s to %s' % (start_date, end_date)
    s_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    e_date = datetime.strptime(end_date, '%Y-%m-%d').date() + \
                                                    timedelta(days=1)
    timeslices = TimeSlice.objects.select_related().filter(
                                user=request.user,
                                begin__range=(s_date, e_date))

    return render_to_response(template_name, {
                'flot_data': flot_timeslices(timeslices, s_date, e_date),
                'headline': headline},
                            context_instance=RequestContext(request))

@user_passes_test(lambda u: u.is_staff)
def billing_index(request, group_slug=None, template_name="djime/statistics/billing_index.html", bridge=None):
    if request.method == 'GET':
        form = BillingSelectionForm()
    elif request.method == 'POST':
        form = BillingSelectionForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            rd = {
                'project_id': cd['project'],
                'task_id': cd['task'],
                'user_id': cd['user'],
                'begin': cd['begin'],
                'end': cd['end'],
            }
            return HttpResponseRedirect(reverse(
                                'djime_statistics_billing_show', kwargs=rd))
    return render_to_response(template_name, {'billing_form': form},
                        context_instance=RequestContext(request))

@user_passes_test(lambda u: u.is_staff)
def billing_show(request, project_id, task_id, user_id, begin, end, group_slug=None, template_name="djime/statistics/billing_info.html", bridge=None):
    if begin != '0':
        s = begin.split('-')
        begin = date(int(s[0]),int(s[1]),int(s[2]))
    else:
        begin = None
    if end != '0':
        e = begin.split('-')
        end = date(int(e[0]),int(e[1]),int(e[2]))
    else:
        end = None
    if project_id == 'all':
        query = Q()
    else:
        query = Q(task__object_id=project_id)
    if task_id == 'all':
        query = query & Q()
    else:
        query = query & Q(task=task_id)
    if user_id == 'all':
        query = query & Q()
    else:
        query = query & Q(user=user_id)
    if begin and end:
        query = query & Q(begin__range=(begin, end + timedelta(days=1)))
    elif begin:
        query = query & Q(begin__gte=begin)
    elif end:
        query = query & Q(begin__gte=end)
    timeslices = TimeSlice.objects.select_related().filter(query)
    return render_to_response(template_name, {'timeslices':
                timesheet_timeslice_handler(timeslices)},
                        context_instance=RequestContext(request))

@login_required()
def flot(request, method=None, year=None, method_value=0):
    result = statistics(request, method=method, year=year, method_value=method_value, ajax=True)
    return HttpResponse(result)