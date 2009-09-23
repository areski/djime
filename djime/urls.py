from django.conf.urls.defaults import *
urlpatterns = patterns('djime.views',
    url(r'^$', 'my_tasks', name='djime_index'),
    url(r'^timesheet/$', 'timesheet', name='djime_timesheet'),
    url(r'^json/project/(?P<project_id>\d+)$', 'project_json', name='djime_project_json'),
)

