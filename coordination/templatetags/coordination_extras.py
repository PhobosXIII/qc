from django import template

from coordination.models import Membership

register = template.Library()


@register.filter
def is_organizer(user, quest):
    user_is_organizer = False
    if user.is_authenticated():
        member = Membership.organizers.filter(quest=quest, user=user).first()
        if member and member.organizer:
            user_is_organizer = True
    return user_is_organizer


@register.filter
def is_player(user, quest):
    user_is_player = False
    if user.is_authenticated():
        member = Membership.players.filter(quest=quest, user=user).first()
        if member and member.player:
            user_is_player = True
    return user_is_player
