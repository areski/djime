
from south.db import db
from django.db import models
from djime.models import *

class Migration:

    def forwards(self, orm):

        # Adding field 'TimeSlice.note'
        db.add_column('djime_timeslice', 'note', models.TextField(null=True, verbose_name=_('note/explanation'), blank=True))

        # Adding field 'Slip.description'
        db.add_column('djime_slip', 'description', models.TextField(blank=True, null=True))

        # Deleting field 'Slip.due'
        db.delete_column('djime_slip', 'due')

        # Deleting field 'TimeSlice.end'
        db.delete_column('djime_timeslice', 'end')

        # Deleting field 'TimeSlice.week_number'
        db.delete_column('djime_timeslice', 'week_number')

        # Changing field 'TimeSlice.begin'
        db.alter_column('djime_timeslice', 'begin', models.DateTimeField(default=datetime.datetime.now, verbose_name=_('start time and date')))

        # Changing field 'TimeSlice.duration'
        db.alter_column('djime_timeslice', 'duration', models.PositiveIntegerField(null=True, verbose_name=_('duration in seconds'), blank=True))



    def backwards(self, orm):

        # Deleting field 'TimeSlice.note'
        db.delete_column('djime_timeslice', 'note')

        # Deleting field 'Slip.description'
        db.delete_column('djime_slip', 'description')

        # Adding field 'Slip.due'
        db.add_column('djime_slip', 'due', models.DateField(null=True, verbose_name=_('due'), blank=True))

        # Adding field 'TimeSlice.end'
        db.add_column('djime_timeslice', 'end', models.DateTimeField(null=True, verbose_name=_('end'), blank=True))

        # Adding field 'TimeSlice.week_number'
        db.add_column('djime_timeslice', 'week_number', models.PositiveIntegerField(default=20, verbose_name=_('week number')))

        # Changing field 'TimeSlice.begin'
        db.alter_column('djime_timeslice', 'begin', models.DateTimeField(default=datetime.datetime.now, verbose_name=_('begin')))

        # Changing field 'TimeSlice.duration'
        db.alter_column('djime_timeslice', 'duration', models.PositiveIntegerField(default=0, editable=False, verbose_name=_('duration')))



    models = {
        'djime.slip': {
            'client': ('models.ForeignKey', ['Client'], {'null': 'True', 'verbose_name': "_('client')", 'blank': 'True'}),
            'created': ('models.DateTimeField', [], {'auto_now_add': 'True', 'verbose_name': "_('created')"}),
            'description': ('models.TextField', [], {'blank': 'True', 'null': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '128', 'verbose_name': "_('name')"}),
            'project': ('models.ForeignKey', ['Project'], {'null': 'True', 'verbose_name': "_('project')", 'blank': 'True'}),
            'updated': ('models.DateTimeField', [], {'auto_now': 'True', 'verbose_name': "_('updated')"}),
            'user': ('models.ForeignKey', ['User'], {'related_name': '"slips"', 'null': 'True', 'verbose_name': "_('user')", 'blank': 'True'})
        },
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'djime.dataimport': {
            'complete_data': ('models.FileField', [], {'verbose_name': "_('complete data')"}),
            'completed': ('models.DateTimeField', [], {'null': 'True', 'verbose_name': "_('completed')", 'blank': 'True'}),
            'created': ('models.DateTimeField', [], {'auto_now_add': 'True', 'verbose_name': "_('created')"}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'partial_data': ('models.FileField', [], {'verbose_name': "_('partial data')"}),
            'user': ('models.ForeignKey', ['User'], {'verbose_name': "_('user')"})
        },
        'project.client': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'project.project': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'djime.timeslice': {
            'begin': ('models.DateTimeField', [], {'default': 'datetime.datetime.now', 'verbose_name': "_('start time and date')"}),
            'duration': ('models.PositiveIntegerField', [], {'null': 'True', 'verbose_name': "_('duration in seconds')", 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'note': ('models.TextField', [], {'null': 'True', 'verbose_name': "_('note/explanation')", 'blank': 'True'}),
            'slip': ('models.ForeignKey', ['Slip'], {'verbose_name': "_('slip')"}),
            'user': ('models.ForeignKey', ['User'], {'related_name': '"timeslices"', 'null': 'True', 'verbose_name': "_('user')", 'blank': 'True'})
        }
    }

    complete_apps = ['djime']
