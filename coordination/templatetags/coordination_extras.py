from django import template

register = template.Library()


@register.filter
def is_organizer(user, quest):
    user_is_organizer = False
    if user.is_authenticated:
        if quest and user == quest.organizer:
            user_is_organizer = True
    return user_is_organizer

@register.filter
def is_player(user, quest):
    user_is_player = False
    if user.is_authenticated:
        if quest and user in quest.players.all():
            user_is_player = True
    return user_is_player