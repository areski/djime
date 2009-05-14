
from south.db import db
from django.db import models
from djime.models import *

class Migration:

    def forwards(self, orm):

        # Adding field 'Project.description'
        db.add_column('project_project', 'description', models.TextField(blank=True, null=True))

    def backwards(self, orm):

        # Deleting field 'Project.description'
        db.delete_column('project_project', 'description')
