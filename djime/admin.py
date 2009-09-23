from django.contrib import admin
from djime.models import TimeSlice, DataImport

class TimeSliceAdmin(admin.ModelAdmin):
    date_hierarchy = 'begin'
    list_display = ('task', 'begin', 'user', 'duration', 'note')
    list_filter = ('task', 'user', 'begin')
    ordering = ('-begin',)

class DataImportAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_display = ('user', 'created', 'completed')
    list_filter = ('user', 'completed')
    ordering = ('-created',)


admin.site.register(TimeSlice, TimeSliceAdmin)
admin.site.register(DataImport, DataImportAdmin)

