import calendar
from datetime import timedelta, date
import datetime
from exceptions import ValueError
from math import floor

from django.contrib.auth.decorators import login_required
from django.http import *
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.core.urlresolvers import reverse

from djime.statistics.forms import DateSelectionForm
from djime.models import TimeSlice
from djime.util import timesheet_timeslice_handler, flot_timeslices
import djime.statistics.flashcharts as flashcharts
from djime.statistics.forms import BillingSelectionForm

try:
    import json
except ImportError:
    from django.utils import simplejson as json

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
def display_user_week(request, user_id, year, week):
    if int(request.user.id) != int(user_id):
        return HttpResponseForbidden(_('Access denied'))
    return render_to_response('statistics/display_user_week.html', {'week': week, 'year': year, 'user_id': user_id},
                                      context_instance=RequestContext(request))


@login_required()
def display_user_month(request, user_id, year, month):
    if int(request.user.id) != int(user_id):
        return HttpResponseForbidden(_('Access denied'))
    return render_to_response('statistics/display_user_month.html', {'month' : month, 'year': year, 'user_id': user_id},
                                      context_instance=RequestContext(request))


@login_required()
def user_date_selection_form(request, user_id):
    if request.method not in ('POST', 'GET'):
        return HttpResponseNotAllowed('POST', 'GET')

    if request.method == 'GET':
        form = DateSelectionForm()
        return render_to_response('statistics/user_date_selection.html', {'user_id': user_id, 'form': form},
                                      context_instance=RequestContext(request))

    if request.method == 'POST':
        form = DateSelectionForm(request.POST)
        if form.is_valid():
            start = form.cleaned_data['start']
            end = form.cleaned_data['end']
            return HttpResponseRedirect('/statistics/user/%s/date/%s/%s/' % (user_id, start, end))
        else:
            return render_to_response('statistics/user_date_selection.html', {'user_id': user_id, 'form': form},
                                      context_instance=RequestContext(request))


@login_required()
def display_user_date_selection(request, user_id, start_date, end_date):
    if int(request.user.id) != int(user_id):
        return HttpResponseForbidden('Access denied')
    s_date = start_date.split('-')
    e_date = end_date.split('-')
    try:
        date_diff = datetime.date(int(e_date[0]), int(e_date[1]), int(e_date[2])) - datetime.date(int(s_date[0]), int(s_date[1]), int(s_date[2]))
        if date_diff < datetime.timedelta(days=60) and date_diff > datetime.timedelta(days=0):
            return render_to_response('statistics/display_user_date.html', {'user_id': user_id, 'start_date': start_date, 'end_date': end_date},
                                          context_instance=RequestContext(request))
        else:
            return HttpResponse(_('Invalid date, min 1 day and max 60 days'))
    except ValueError:
        return HttpResponse(_('Invalid date, must be yyyy-mm-dd'))


def data_user_week(request, week, year, user_id):
    if request.method != 'GET':
         return HttpResponseNotAllowed('GET')

    week = int(week)
    year = int(year)
    return HttpResponse(flashcharts.user_week_json(request.user, week, year))


def data_user_month(request, month, year, user_id):
    if request.method != 'GET':
         return HttpResponseNotAllowed('GET')

    month = int(month)
    year = int(year)
    return HttpResponse(flashcharts.user_month_json(request.user, month, year))


def data_user_date(request, user_id, start_date, end_date):
    return HttpResponse(flashcharts.user_date_json(request.user, start_date, end_date))









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
            return HttpResponseRedirect(reverse('djime_statistics_billing_show', kwargs=rd))
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
def user_billing(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'GET':
        return render_to_response('statistics/billing_time_page.html', {'sellected_user': user, 'form': DateSelectionForm()},
                            context_instance=RequestContext(request))
    elif request.method == 'POST':
        post = request.POST
        if request.POST.has_key('number-of-weeks'):
            date = request.POST['start-date']
            number_of_weeks = request.POST['number-of-weeks']
            if not re.match("[0-9]{4}[-]{1}[0-9]{2}[-]{1}[0-9]{2}$", request.POST['start-date']):
                request.user.message_set.create(message=_("Invalid date format, must be yyyy-mm-dd."))
                return render_to_response('statistics/billing_time_page.html', {'sellected_user': user, 'form': DateSelectionForm()},
                                          context_instance=RequestContext(request))
            return HttpResponseRedirect('/statistics/billing/%s/week/%s/%s/' % (user_id, date, number_of_weeks))
            raise
        elif request.POST.has_key('date'):
            form = DateSelectionForm(request.POST)
            if form.is_valid():
                start = form.cleaned_data['start']
                end = form.cleaned_data['end']
                return HttpResponseRedirect('/statistics/billing/%s/date/%s/%s/' % (user_id, start, end))
            else:
                return render_to_response('statistics/billing_time_page.html', {'sellected_user': user, 'form': form},
                                          context_instance=RequestContext(request))


@login_required()
def user_billing_weeks(request, user_id, date, number_of_weeks):
    user = get_object_or_404(User, pk=user_id)
    if number_of_weeks > 5:
        number_of_weeks = 4
    date_list = date.split('-')
    try:
        start_date = datetime.date(int(date_list[0]), int(date_list[1]), int(date_list[2]))
    except ValueError:
        return HttpResponse(_('Invalid date, must be yyyy-mm-dd'))
    end_date = start_date + datetime.timedelta(days=number_of_weeks*7)
    slice_set = TimeSlice.objects.filter(user=user, begin__range=(start_date, end_date))
    project_dict = {}
    for time_slice in slice_set:
        if time_slice.slip.project not in project_dict.keys():
            project_dict[time_slice.slip.project] = {}
            project_dict[time_slice.slip.project]['slips'] = {}
            project_dict[time_slice.slip.project]['slips'][time_slice.slip] = [time_slice.slip, time_slice.duration]
            project_dict[time_slice.slip.project]['duration'] = time_slice.duration
            project_dict[time_slice.slip.project]['project'] = time_slice.slip.project
        else:
            if time_slice.slip not in project_dict[time_slice.slip.project]['slips'].keys():
                project_dict[time_slice.slip.project]['slips'][time_slice.slip] = [time_slice.slip, time_slice.duration]
                project_dict[time_slice.slip.project]['duration'] += time_slice.duration
            else:
                project_dict[time_slice.slip.project]['slips'][time_slice.slip][1] += time_slice.duration
                project_dict[time_slice.slip.project]['duration'] += time_slice.duration

    for key in project_dict.keys():
        project_dict[key]['duration'] = '%02i:%02i' % (floor(project_dict[key]['duration'] / 3600), floor(project_dict[key]['duration'] % 3600 ) / 60)
        for key_slip in project_dict[key]['slips'].keys():
            project_dict[key]['slips'][key_slip][1] = '%02i:%02i' % (floor(project_dict[key]['slips'][key_slip][1] / 3600), floor(project_dict[key]['slips'][key_slip][1] % 3600 ) / 60)

    return render_to_response('statistics/billing_page.html', {'user': user, 'start_date': start_date, 'end_date': end_date, 'project_dict': project_dict},
                                context_instance=RequestContext(request))


def user_billing_date(request, user_id, start_date, end_date):
    user = get_object_or_404(User, pk=user_id)
    try:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponse('Invalid dateformat, must be yyyy-mm-dd')
    slice_set = TimeSlice.objects.filter(user=user, begin__range=(start_date, end_date))
    project_dict = {}
    for time_slice in slice_set:
        if time_slice.slip.project not in project_dict.keys():
            project_dict[time_slice.slip.project] = {}
            project_dict[time_slice.slip.project]['slips'] = {}
            project_dict[time_slice.slip.project]['slips'][time_slice.slip] = [time_slice.slip, time_slice.duration]
            project_dict[time_slice.slip.project]['duration'] = time_slice.duration
            project_dict[time_slice.slip.project]['project'] = time_slice.slip.project
        else:
            if time_slice.slip not in project_dict[time_slice.slip.project]['slips'].keys():
                project_dict[time_slice.slip.project]['slips'][time_slice.slip] = [time_slice.slip, time_slice.duration]
                project_dict[time_slice.slip.project]['duration'] += time_slice.duration
            else:
                project_dict[time_slice.slip.project]['slips'][time_slice.slip][1] += time_slice.duration
                project_dict[time_slice.slip.project]['duration'] += time_slice.duration

    for key in project_dict.keys():
        project_dict[key]['duration'] = '%02i:%02i' % (floor(project_dict[key]['duration'] / 3600), floor(project_dict[key]['duration'] % 3600 ) / 60)
        for key_slip in project_dict[key]['slips'].keys():
            project_dict[key]['slips'][key_slip][1] = '%02i:%02i' % (floor(project_dict[key]['slips'][key_slip][1] / 3600), floor(project_dict[key]['slips'][key_slip][1] % 3600 ) / 60)

    return render_to_response('statistics/billing_page.html', {'user': user, 'start_date': start_date, 'end_date': end_date, 'project_dict': project_dict},
                                context_instance=RequestContext(request))

