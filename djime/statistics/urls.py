from django.conf.urls.defaults import *

urlpatterns = patterns('djime.statistics.views',
    url(r'^$', 'index', name='djime_statistics_index'),
    url(r'^(?P<method>(week|month|quarter|year))/$', 'statistics', name='djime_this_wmqy_statistics'),
    url(r'^(?P<method>(week|month|quarter|year))/(?P<method_value>\d{1,4})/$', 'statistics', name='djime_wmqy_statistics'),
    url(r'^(?P<method>(week|month|quarter))/(?P<method_value>[1-9]|[1-4][0-9]|5[0-3])/year/(?P<year>\d{4,4})/$', 'statistics', name='djime_wmq_statistics'),
    url(r'^select/$', 'statistics_select_form', name='djime_select_statistics'),
    url(r'^date/(?P<start_date>[0-9-]+)/(?P<end_date>[0-9-]+)/$', 'statistics_date', name='djime_date_statistics'),

    url(r'^billing/$', 'billing_index', name='djime_statistics_billing_index'),
    url(r'^billing/project/(?P<project_id>\d+|all)/tesk/(?P<task_id>\d+|all)/user/(?P<user_id>\d+|all)/(?P<begin>[0-9-]+)/(?P<end>[0-9-]+)/$', 'billing_show', name='djime_statistics_billing_show'),

    url(r'^ajax/flot/(?P<method>(week|month|quarter|year))/(?P<method_value>\d{1,4})/$', 'flot', name='djime_wmqy_flot'),
    url(r'^ajax/flot/(?P<method>(week|month|quarter))/(?P<method_value>[1-9]|[1-4][0-9]|5[0-3])/year/(?P<year>\d{4,4})/$', 'flot', name='djime_wmq_flot'),
)
