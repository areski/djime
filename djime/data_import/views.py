import cPickle as pickle

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as trans

from djime.data_import.forms import DataImportForm
from djime.models import DataImport
from djime.data_import.importer import pinax_handle_uploaded_file, importer_save
from djime.models import TimeSlice


@login_required
def import_form(request, group_slug=None, template_name="djime/data_import/upload.html", bridge=None):
    if request.method == 'POST':
        form = DataImportForm(request.POST, request.FILES)

        if form.is_valid():
            import_id = pinax_handle_uploaded_file(request.FILES['import_file'], request.user.id)
            action = 'confirm'
            return HttpResponseRedirect(reverse('djime_data_import_action', args=(import_id, action)))
    else:
        form = DataImportForm()
    return render_to_response(template_name, {'djime_data_import_form': form},
                              context_instance=RequestContext(request))
@login_required
def action(request, import_id, action, group_slug=None, template_name="djime/data_import/confirm.html", bridge=None):
    import_data = get_object_or_404(DataImport, pk=import_id, completed=None)
    if request.user.id != import_data.user_id:
        return HttpResponseForbidden(trans('Access denied'))

    if request.method == 'GET':
        if action == 'confirm':
            preview_data = pickle.loads(import_data.partial_data.read())
            return render_to_response(template_name,
                                      {'import_data': preview_data, 'import_id': import_id},
                                      context_instance=RequestContext(request))

    if request.method == 'POST':
        if action == 'save':
            importer_save(import_data, request.user)
            request.user.message_set.create(message=trans('Import successful'))
        elif action == 'cancel':
            import_data.delete()
            request.user.message_set.create(message=trans('Import cancelled'))
        else:
            return HttpResponseForbidden(trans('Invalid post action'))

        return HttpResponseRedirect(reverse('djime_index'))

