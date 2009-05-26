from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext as trans
from django.utils.html import escape

from project.forms import ProjectUpdateForm, ProjectAddForm, ClientAddForm
from project.models import Project, Client
from teams.models import Team
from djime.models import Slip, TimeSlice

try:
    import json
except ImportError:
    from django.utils import simplejson as json

@login_required()
def index(request):
    # Data returned to the template
    data = {
            'projects_active': Project.objects.filter(members=request.user, state='active').order_by('name'),
            'projects_on_hold': Project.objects.filter(members=request.user, state='on_hold').order_by('name'),
            'projects_completed': Project.objects.filter(members=request.user, state='completed').order_by('name'),
            'projects_dropped': Project.objects.filter(members=request.user, state='dropped').order_by('name'),
            }
    # Adding a form to create a new project if user is viewing this page.
    if request.method == 'GET':
        data['project_add_form'] = ProjectAddForm()
    # Handleing the form data that's being posted.
    elif request.method == 'POST':
        form = ProjectAddForm(request.POST)
        if form.is_valid:
            new_project = form.save()
            # Need to save the new project before we can assign the user to the project.
            new_project.members.add(request.user)
            new_project.save()
            return HttpResponseRedirect(reverse('project_page', kwargs={'project_id': new_project.id}))
        # if form doesn't validate, return the form with errors.
        else:
            data['project_add_form'] = form
    return render_to_response('project/project_index.html', data,
                                         context_instance=RequestContext(request))




@login_required()
def show_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.user not in project.members.all():
        return HttpResponseForbidden(trans('Access Denied'))
    # Data returned to the template.
    data = {
        'project': project,
    }
    # We get the data we need based on TimeSlice so we can follow the
    # foreignkeys we need to follow.
    slice_all =  TimeSlice.objects.select_related('slip', 'user').filter(slip__project=project)
    slip_user = {}
    slip_rest = {}

    # Here duration for project's slips is calculated by iterating over all the
    # timeslice. While asociating each timeslice to it's slip.

    duration_all = 0
    duration_user = 0
    duration_rest = 0
    for slice in slice_all:
        duration_all += slice.duration
        if slice.user == request.user:
            duration_user += slice.duration
            if slice.slip not in slip_user.keys():
                slip_user[slice.slip] = slice.duration
            else:
                slip_user[slice.slip] += slice.duration
        else:
            duration_rest += slice.duration
            if slice.slip not in slip_rest.keys():
                slip_rest[slice.slip] = slice.duration
            else:
                slip_rest[slice.slip] += slice.duration

    # Formating the display of the time, to make it more human readable.
    data['time_all'] ='%02i:%02i' % (duration_all/3600, duration_all%3600/60)
    data['time_user'] ='%02i:%02i' % (duration_user/3600, duration_user%3600/60)
    data['time_other'] ='%02i:%02i' % (duration_rest/3600, duration_rest%3600/60)
    for slip in slip_user.keys():
        slip_user[slip] = '%02i:%02i' % (slip_user[slip]/3600, slip_user[slip]%3600/60)
    for slip in slip_rest.keys():
        slip_rest[slip] = '%02i:%02i' % (slip_rest[slip]/3600, slip_rest[slip]%3600/60)

    # run the slips lists through the slip_list_improved template as a sting
    # to create a list display of the slips as a template variable. This is
    # repeated for the remaining slips in the project aswell.
    # Note, when the 10_paginate variable is set to TRUE, a pagination
    # displaying 10 items per page instead of the default 20.
    if slip_user:
        data['user_list'] = render_to_string('djime/slip_list_improved.html',
                              {'slip_list': slip_user, '10_paginate': True,
                               'list_exclude_project': True,
                               'list_exclude_client': True,
                              },
                              context_instance=RequestContext(request))

    if slip_rest:
        data['other_list'] = render_to_string('djime/slip_list_improved.html',
                              {'slip_list': slip_rest, '10_paginate': True,
                               'list_exclude_project': True,
                               'list_exclude_client': True,
                              },
                              context_instance=RequestContext(request))

    # Adding a form to update the project, if the page is being viewed.
    if request.method == 'GET':
        data['form'] = ProjectUpdateForm()
        return render_to_response('project/project.html', data,
                              context_instance=RequestContext(request))

    if request.method == 'POST':
        form = ProjectUpdateForm(request.POST, instance=project)
        # if the form validates, a new form is displayed for the user, if not
        # the form is redisplayed with errors.
        if form.is_valid():
            test = form.save()
            data['form'] = ProjectUpdateForm()
            data['project'] = Project.objects.get(pk=project_id)
        else:
            data['form'] = form
        return render_to_response('project/project.html', data,
                                      context_instance=RequestContext(request))


@login_required()
def client_index(request):
    if request.method == 'GET':
        clients = Client.objects.all()
        return render_to_response('project/client_index.html', {'clients': clients, 'client_add_form': ClientAddForm()},
                                        context_instance=RequestContext(request))

    elif request.method == 'POST':
        form = ClientAddForm(request.POST)
        if form.is_valid():
            new_client = form.save()
            return HttpResponseRedirect(reverse('client_page', kwargs={'client_id': new_client.id}))
        else:
            return render_to_response('project/client_index.html', {'client_add_form': form},
                                         context_instance=RequestContext(request))


@login_required()
def show_client(request, client_id):
    # this view is pretty much the same as the  show_project view, only in this
    # case, a form to update the client is not being presented.

    client = get_object_or_404(Client, pk=client_id)
    data = {
        'client': client,
    }
    projects = Project.objects.filter(client=client, members=request.user)
    data['slip_all'] = Slip.objects.filter(project__in=projects)
    data['slip_user'] = data['slip_all'].filter(user=request.user)
    data['slip_rest'] = data['slip_all'].exclude(user=request.user)
    duration = 0
    for slip in data['slip_all']:
        seconds = 0
        for slice in slip.timeslice_set.all():
            seconds += slice.duration
        duration += seconds
    data['time_all'] ='%02i:%02i' % (duration/3600, duration%3600/60)
    duration = 0
    for slip in data['slip_user']:
        seconds = 0
        for slice in slip.timeslice_set.all():
            seconds += slice.duration
        duration += seconds
    data['time_user'] ='%02i:%02i' % (duration/3600, duration%3600/60)
    duration = 0
    for slip in data['slip_rest']:
        seconds = 0
        for slice in slip.timeslice_set.all():
            seconds += slice.duration
        duration += seconds
    data['time_other'] ='%02i:%02i' % (duration/3600, duration%3600/60)

    data['user_list'] = render_to_string('djime/slip_list.html',
                              {'slip_list': data['slip_user'], '10_paginate': True,
                              'list_exclude_client': True
                              },
                              context_instance=RequestContext(request))

    data['other_list'] = render_to_string('djime/slip_list.html',
                              {'slip_list': data['slip_rest'], '10_paginate': True,
                              'list_exclude_client': True
                              },
                              context_instance=RequestContext(request))

    data['project_list'] = client.project_set.filter(state__in=['active', 'on_hold'], members=request.user)

    return render_to_response('project/client.html', data,
                                      context_instance=RequestContext(request))

def project_json(request):
    # this view is only to be used by javascript ajax call to generate data to
    # be used by jquery autocomplete function.
    # Client list is to be used to create a js array. So we need an initial
    # value for position 0. This value should not be 0+ so -1 is chosen. could
    # be anything really.
    client_list = [-1]
    client_dict = {}
    project_list = Project.objects.filter(members=request.user, state__in=['active', 'on_hold'])
    for project in project_list:
        if project.client:
            if not client_dict.has_key((project.client.id)):
                client_dict[(project.client.id)] = []
                client_dict[(project.client.id)].append(project)
            else:
                client_dict[(project.client.id)].append(project)
    # this loop is to create a set of options tags, the first will will be the
    # choice for nothing and will have a value of a empty string. The rest will
    # have same value as their name. Escape is used on rojectname because we
    # need to use the json version unescaped in the template.
    if Client.objects.all():
        client_id_max = Client.objects.all().order_by('-id')[0].id
        for client_id in range(1, client_id_max+1):
            if client_dict.has_key(client_id):
                options = '<option value="">-----------</option>'
                for project in client_dict[client_id]:
                    options += '<option>%s</option>' % escape(project.name)
                client_list.append(options)
            else:
                client_list.append(0)
    # now converting the project list into the escaped names that is to be used
    # later in the js autocomplate function.
    project_escaped_list = []
    for project in project_list:
        if project.client:
            project_escaped_list.append([escape(project.name), str(project.client.id)])
        else:
            project_escaped_list.append([escape(project.name), ''])
    return_data = [project_escaped_list, client_list]
    return HttpResponse(json.dumps(return_data))
