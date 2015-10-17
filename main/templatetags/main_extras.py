from django import template
from django.core.urlresolvers import reverse

register = template.Library()


@register.inclusion_tag('tags/menu_item.html', takes_context=True)
def menu_item(context, link_text, named_url = None):
    active = False
    item_url = '#'
    request = context['request']
    if named_url:
        item_url = reverse(named_url)
        if item_url:
            if request.path == item_url:
                active = True
    return {'item_url': item_url, 'link_text': link_text, 'active': active}
