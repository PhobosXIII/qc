from django import template

register = template.Library()


@register.filter
def is_organizer(user, quest):
    user_is_organizer = False
    if user.is_authenticated:
        if quest and user == quest.organizer:
            user_is_organizer = True
    return user_is_organizer
