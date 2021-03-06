from datetime import datetime

from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User


class Team(models.Model):
    """
    a tribe is a group of users with a common interest
    """

    slug = models.SlugField(_('slug'), unique=True)
    name = models.CharField(_('name'), max_length=80, unique=True)
    creator = models.ForeignKey(User, related_name="created_groups", verbose_name=_('creator'))
    created = models.DateTimeField(_('created'), default=datetime.now)
    description = models.TextField(_('description'))
    members = models.ManyToManyField(User, verbose_name=_('members'))

    deleted = models.BooleanField(_('deleted'), default=False)


    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return ("team_display", [self.slug])
    get_absolute_url = models.permalink(get_absolute_url)
