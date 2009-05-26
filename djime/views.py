from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import *
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.html import escape
from django.utils.translation import ugettext as trans

from djime.models import Slip, TimeSlice
from djime.forms import SlipForm, TimeSliceForm, TimeSliceSheetForm
from project.models import Client, Project

try:
    import json
except ImportError:
    from django.utils import simplejson as json


@login_required()
def dashboard(request):
    display_data = {
        'slip_list': Slip.objects.filter(user=request.user).order_by('-updated')[:10],
        'project_list': Project.objects.filter(members=request.user.id, state='active')[:10],
        'slip_add_form': SlipForm()
    }
    return render_to_response('djime/index.html', display_data,
                              context_instance=RequestContext(request))


@login_required
def index(request):
    slice_list = TimeSlice.objects.select_related('slip', 'slip__project', 'slip__project__client').filter(user=request.user)
    slips = {}
    for slice in slice_list:
        if slice.slip not in slips.keys():
            slips[slice.slip] = slice.duration
        else:
            slips[slice.slip] += slice.duration
    slip_list = []
    for slip in slips:
        slip_list.append({slip: '%02i:%02i' % (slips[slip]/3600, slips[slip]%3600/60)})
    return render_to_response('djime/slip_index.html', {
            'slip_list': slip_list,
            'slip_add_form': SlipForm()
        }, context_instance=RequestContext(request))


@login_required
def time_sheet_index(request):
    today = datetime.now()
    if request.is_ajax():
        json = ''
        for slip in Slip.objects.filter(user=request.user,
                            project=request.POST['project']).order_by('name'):
            json += '<option value="%(id)s">%(name)s</option>' % {
                                            'id': slip.id, 'name': slip.name}
        return HttpResponse(json)
    display_data = {
        'slice_list': TimeSlice.objects.select_related().filter(
                            user=request.user, begin__day=today.day,
                            begin__month=today.month, begin__year=today.year),
        'slip_add_form': SlipForm()
    }
    if request.method == 'GET':
        display_data['timesheet_timeslice_form'] = TimeSliceSheetForm(request.user)
    if request.method == 'POST':
        form = TimeSliceSheetForm(request.user, request.POST)
        if form.is_valid():
            clean = form.cleaned_data
            timeslice = TimeSlice(begin=datetime.now(),
                                    duration=clean['duration'],
                                    note=clean['note'],
                                    slip=clean['slip'],
                                    user=request.user)
            timeslice.save()
        else:
            display_data['timesheet_timeslice_form'] = form
    return render_to_response('djime/time_sheet_index.html', display_data,
                                      context_instance=RequestContext(request))


@login_required()
def slip(request, slip_id):
    valid_methods = ('GET', 'POST', 'DELETE')

    if request.method not in valid_methods:
        return HttpResponseNotAllowed(('GET', 'POST', 'DELETE'))

    slip = get_object_or_404(Slip, pk=slip_id)

    if request.user != slip.user:
        return HttpResponseForbidden(trans('Access denied'))

    if request.method == 'DELETE':
        slip.delete()
        # TODO: Send a message to the user that deltion succeeded.
        return HttpResponse('Successfully deleted slip %s' % slip.name)

    elif request.method == 'POST':
        form = SlipForm(request.POST, instance=slip)
        
        if form.is_valid():
            slip = form.save()

            if request.is_ajax():
                if not request.POST.has_key('project'):
                    return HttpResponse(slip.name)
                return HttpResponse("slip/%s" % slip.id)
            else:
                return HttpResponseRedirect(reverse('slip_page',
                                                    kwargs={'slip_id': slip.id}))
    else:
        form = SlipForm(instance=slip)

    timer_class = ''
    if slip.is_active():
        timer_class = 'timer-running'
    return render_to_response('djime/slip.html',
                                            {'slip': slip,
                                            'slip_change_form': form,
                                            },
                                            context_instance=RequestContext(request))

@login_required()
def slip_action(request, slip_id, action):
    if request.method not in ('GET', 'POST'):
        return HttpResponseNotAllowed(('POST', 'GET'))

    # make sure the slip exists
    slip = get_object_or_404(Slip, pk=slip_id)

    # only the slip owner may modify it
    if request.user != slip.user:
        return HttpResponseForbidden(trans('Access denied'))

    if action == 'start':
        # Make sure the user doesn't already have an active time slice
        # for this Slip
        if not TimeSlice.objects.filter(user=request.user,
                                        slip=slip_id, duration=None):
            if request.POST.has_key('begin'):
                start_time = 0
                time = request.POST['begin']
                if type(time) == unicode:
                    time = time.split(', ')
                    start_time = datetime(int(time[0]), int(time[1]), int(time[2]), int(time[3]), int(time[4]), int(time[5]), int(time[6]))
                else:
                    start_time = datetime.now()
            else:
                start_time = datetime.now()

            # Stop active timeslices if any
            slice_query_set = TimeSlice.objects.filter(user=request.user, duration=None)
            if slice_query_set:
                for slice in slice_query_set:
                    slice.calculate_duration()
                    slice.save() # updates duration and saves the timeslice using signals.py

            new_slice = TimeSlice.objects.create(user=request.user, slip_id=slip_id, begin=start_time)
            new_slice.save()
            return HttpResponse(trans('Your timeslice begin time %(start_time)s has been created') % {'start_time': start_time})
        else:
            return HttpResponse(trans('You already have an unfinished time slice for this task. A new one has not been created.'), status=409)

    elif action == 'stop':
        time_slice = TimeSlice.objects.get(user=request.user, slip=slip_id, duration=None)
        if request.POST.has_key('end'):
            time = request.POST['end']
            if type(time) == unicode:
                time = time.split(', ')
                end_time = datetime(int(time[0]), int(time[1]), int(time[2]), int(time[3]), int(time[4]), int(time[5]), int(time[6]))
        else:
            end_time = datetime.now()
        time_slice.calculate_duration(end_time)
        time_slice.save()
        return HttpResponse(trans('Your timeslice for slip "%(name)s", begintime %(begin)s has been stopped at %(end)s') % {'name': time_slice.slip.name, 'begin': time_slice.begin, 'end': end_time})

    elif action == 'get_json':
        if slip.is_active() == False:
            return HttpResponse("{'active' : true, 'slip_time' : '%s' }" % slip.display_time())
        else:
           return HttpResponse("{'active' : false, 'slip_time' : '%s' }" % slip.display_time())

    else:
        #Make a return for only action allowed is start/stop
        pass

@login_required()
def slip_create(request):
    if request.method not in ('GET', 'POST'):
        return HttpResponseNotAllowed(('POST', 'GET'))

    if request.method == 'POST':
        post_data = request.POST.copy()
        # Inject the user into the post data, so we can validate based
        # on the user.
        post_data['user'] = request.user

        form = SlipForm(post_data)
        if form.is_valid():
            new_slip = form.save(commit=False)
            new_slip.user = request.user
            new_slip.save()
            # We check to see if the post is comming from ajax or the form on slip/add.
            # The post dict will have the key 'ajax' added when it's being
            # generated by the javascript.
            if request.is_ajax():
                return HttpResponse("slip/%s" % new_slip.pk)
            else:
                return HttpResponseRedirect(reverse('slip_page',
                                                    kwargs={'slip_id': new_slip.id}))

        else:
            return render_to_response('djime/slip_create.html',
                                        {'slip_add_form': form,
                                        },
                                        context_instance=RequestContext(request))

    if request.method == 'GET':
        slip_add_form = SlipForm()
        return render_to_response('djime/slip_create.html',
                                  {'slip_add_form': slip_add_form,
                                  },
                                  context_instance=RequestContext(request))

@login_required()
def time_slice_create(request, slip_id):
    if request.method not in ('GET', 'POST'):
        return HttpResponseNotAllowed(('POST', 'GET'))

    slip = get_object_or_404(Slip, pk=slip_id)
    
    if request.method == 'POST':
        form = TimeSliceForm(request.POST)
        if form.is_valid():
            time_slice = TimeSlice.objects.create(slip=slip, user=request.user)
            form.update_model(time_slice)
            time_slice.save()

            if request.is_ajax():
                return HttpResponse('Successfully created slice %s' % new_slice.id )
            else:
                return HttpResponseRedirect(reverse('slip_page',
                                                    kwargs={'slip_id': slip.id}))


    else:
        time_slice_add_form = TimeSliceForm({'begin':datetime.now(), 'end': datetime.now()})

    return render_to_response('djime/time_slice_create.html',
                              {'time_slice_add_form': form,
                               'slip': slip,
                              },
                              context_instance=RequestContext(request))

@login_required()
def time_slice(request, slip_id, time_slice_id):
    valid_methods = ('GET', 'POST', 'DELETE')

    if request.method not in valid_methods:
        return HttpResponseNotAllowed(('GET', 'POST', 'DELETE'))

    slip = get_object_or_404(Slip, pk=slip_id)

    time_slice = get_object_or_404(slip.timeslice_set, pk=time_slice_id)

    if request.user != slip.user:
        return HttpResponseForbidden(trans('Access denied'))

        return render_to_response('djime/time_slice.html',
                                    {'time_slice': time_slice,
                                    'time_slice_change_form': form,
                                    'slip': slip,
                                    },
                                    context_instance=RequestContext(request))

    elif request.method == 'DELETE':
        time_slice.delete()
        # TODO: Send a message to the user that deltion succeeded.
        if request.is_ajax():
            return HttpResponse('Successfully deleted time slice %s' % time_slice.name)
        else:
            return HttpResponseRedirect(reverse('slip_page',
                                                    kwargs={'slip_id': slip.id}))

    elif request.method == 'POST':
        form = TimeSliceForm(request.POST)
        if form.is_valid():
            form.update_model(time_slice)
            time_slice.save()

            if request.is_ajax():
                return HttpResponse('Successfully saved time slice %s' % time_slice.id)
            else:
                return HttpResponseRedirect(reverse('slip_page',
                                                    kwargs={'slip_id': slip.id}))
    else:
        form = TimeSliceForm(instance=time_slice)

    return render_to_response('djime/time_slice.html',
                                {'time_slice': time_slice,
                                'time_slice_change_form': form,
                                'slip': slip,
                                },
                                context_instance=RequestContext(request))
