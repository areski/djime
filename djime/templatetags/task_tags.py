from django import template
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

register = template.Library()


def do_get_users_time(parser, token):
    """
    Get the amount of time a user has spent on a task
    """
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, task, user = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly two arguments" % token.contents.split()[0]
    
    return GetUsersTimeNode(task, user)

class GetUsersTimeNode(template.Node):
    def __init__(self, task, user):
        self.task = template.Variable(task)
        self.user = template.Variable(user)

    def render(self, context):
        try:
            task = self.task.resolve(context)
            user = self.user.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        return task.display_user_time(user)

register.tag('get_users_time', do_get_users_time)
