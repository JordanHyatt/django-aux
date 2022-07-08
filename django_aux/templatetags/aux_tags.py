from django import template

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    ''' A custom template tag for determining group permissions in templates '''
    return user.groups.filter(name=group_name).exists()


@register.filter
def has_rows(table):
    ''' A custom template tag that returns true if the django table has any entries '''
    return True if table.rows.__len__() > 0 else False


@register.filter
def has_items(container):
    ''' A custom template tag that takes an iterable returns true if len > 0 '''
    return True if len(container) > 0 else False

@register.filter
def render_class_name(obj):
    ''' A custom template tag that returns the object's class' name '''
    return obj.__class__.__name__
