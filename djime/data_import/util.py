from datetime import datetime

from django.template.defaultfilters import slugify
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from projects.models import Project, ProjectMember

def create_pinax_project(user, line):
    project = Project()
    project.creator = user
    project.name = line['project']
    project.slug = slugify(line['project'])
    project_created_msg = _('Found more than one project, you are on, with same name. New project will be created.')
    project_created_bool = True
    return (project, project_created_msg, project_created_bool)