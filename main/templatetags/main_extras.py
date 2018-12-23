from django import template
from django.urls import reverse
from django.utils.encoding import force_text

register = template.Library()


@register.inclusion_tag('tags/menu_item.html', takes_context=True)
def menu_item(context, link_text, named_url=None, *args, **kwargs):
    contains = kwargs.pop('contains', False)
    active = False
    item_url = '#'
    request = context['request']
    if named_url:
        item_url = reverse(named_url, args=args)
        if contains:
            if item_url and item_url in request.path:
                active = True
        else:
            if item_url and request.path == item_url:
                active = True
    return {'item_url': item_url, 'link_text': link_text, 'active': active}


@register.filter
def in_group(user, groups):
    if user.is_authenticated():
        group_list = force_text(groups).split(',')
        return bool(user.groups.filter(name__in=group_list).values('name'))
    else:
        return False
