import datetime
def timeslice_save(sender, **kwargs):
    time_slice = kwargs['instance']
    time_slice.slip.updated = datetime.datetime.now()
    time_slice.user = time_slice.slip.user
    time_slice.slip.save()

