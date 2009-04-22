from south.db import db
from django.db import models
from djime.models import *
import datetime

class Migration:
    """
    Migration for a rather large database refactoring.

     * Added a description field to the Slip.
     * Removed the due field from the Slip.
     * Made the duration field on the TimeSlice nullable.
     * NULL the duration where it is less than 1.
     * Updating the duration with the data from the end field.
     * Added a note field on the TimeSlice.
     * Removed the end field from the TimeSlice.
    """
    def forwards(self):
        pass

    def backwards(self):
        pass

