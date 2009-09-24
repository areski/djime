from django.conf.urls.defaults import *

urlpatterns = patterns('djime.data_import.views',
    url(r'^$', 'import_form', name='djime_data_import_form'),
    url(r'^(?P<import_id>\d+)/(?P<action>(confirm|save|cancel))/$',
        'action', name='djime_data_import_action'),
)

