from django.conf.urls.defaults import *
urlpatterns = patterns('djime.views',
    url(r'^$', 'my_tasks', name='djime_index'),
    url(r'^timesheet/$', 'timesheet', name='djime_timesheet'),
    url(r'^timesheet/(?P<method>(week|month|quarter|year))/$', 'timesheet', name='djime_this_wmqy_timesheet'),
    url(r'^timesheet/(?P<method>(week|month|quarter|year))/(?P<method_value>\d{1,4})/$', 'timesheet', name='djime_wmqy_timesheet'),
    url(r'^timesheet/(?P<method>(week|month|quarter))/(?P<method_value>[1-9]|[1-4][0-9]|5[0-3])/year/(?P<year>\d{4,4})/$', 'timesheet', name='djime_wmq_timesheet'),
    url(r'^timesheet/date/(?P<start_date>[0-9-]+)/(?P<end_date>[0-9-]+)/$', 'timesheet_date', name='djime_date_timesheet'),
    url(r'^timesheet/select/$', 'timesheet_select_form', name='djime_select_timesheet'),
    url(r'^timetrack/$', 'timetrack', name='djime_timetrack'),
    url(r'^json/project/(?P<project_id>\d+)$', 'project_json', name='djime_project_json'),
    url(r'^ajax/task/(?P<task_id>\d+)/(?P<action>(start|stop|get_json))/$', 'task_action', name='djime_task_action'),
)

urlpatterns += patterns('djime.statistics.views', (r'^statistics/', include('djime.statistics.urls')))