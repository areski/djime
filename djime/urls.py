from django.conf.urls.defaults import *
urlpatterns = patterns('djime.views',
    url(r'^$', 'my_tasks', name='djime_index'),
    url(r'^timesheet/$', 'timesheet', name='djime_timesheet'),
)

