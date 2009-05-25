from django.conf.urls.defaults import *

urlpatterns = patterns('djime.views',
    url(r'^$', 'dashboard', name='djime_index'),
    url(r'^slip/$', 'index', name="slip_index"),
    url(r'^slip/(?P<slip_id>\d+)/$', 'slip', name="slip_page"),
    url(r'^slip/(?P<slip_id>\d+)/(?P<action>(start|stop|get_json))/$',
        'slip_action', name="slip_action"),
    url(r'^slip/(?P<slip_id>\d+)/slice/(?P<time_slice_id>\d+)/$',
        'time_slice', name="time_slice_page"),
    url(r'^slip/(?P<slip_id>\d+)/slice/add$',
        'time_slice_create', name="time_slice_create"),
    url(r'^slip/add', 'slip_create', name="slip_create"),
    url(r'^sheet/$', 'time_sheet_index', name='time_sheet_index'),
    (r'^import/', include('djime.data_import.urls')),
    (r'^statistics/', include('djime.statistics.urls')),
)

