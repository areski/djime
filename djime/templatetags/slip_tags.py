from django import template
from django.utils.translation import ugettext_lazy as _

register = template.Library()

def do_get_time_slice(parser, token):
    """
    retrieve all time slices to a slip and add them to the context.
    """
    bits = token.contents.split()
    
    if len(bits) not in (2,4):
        raise template.TemplateSyntaxError( _("%(tag_name)r tag takes 1 or 3 arguments. {% %(tag_name)r slip [ as context_var] %}"))

    context_name = None
    if len(bits) == 4:
        context_name = bits[3]
    return GetTimeSlicesNode(bits[1], context_name )
    
class GetTimeSlicesNode(template.Node):
    def __init__(self, slip, context_name):
        self.slip      = template.Variable(slip)
        self.context_name = context_name

    def get_context_name(self, context):
        name = 'time_slices'
        if self.context_name <> None:
            name = template.Variable(self.context_name).resolve( context )
        return name

    def render(self, context):
        context[self.get_context_name( context )] = self.slip.resolve( context ).timeslice_set.all()
        return ''

register.tag('get_time_slices', do_get_time_slice)
