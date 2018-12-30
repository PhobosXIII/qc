import math
from django import template

from coordination.models import Membership

register = template.Library()


@register.filter
def is_organizer(user, quest):
    user_is_organizer = False
    if user.is_authenticated:
        if quest.parent:
            quest = quest.parent
        member = Membership.organizers.filter(quest=quest, user=user).first()
        if member:
            user_is_organizer = True
    return user_is_organizer


@register.filter
def is_player(user, quest):
    user_is_player = False
    if user.is_authenticated:
        if quest.parent:
            quest = quest.parent
        member = Membership.players.filter(quest=quest, user=user).first()
        if member:
            user_is_player = True
    return user_is_player


@register.filter
def is_agent(user, quest):
    user_is_agent = False
    if user.is_authenticated:
        if quest.parent:
            quest = quest.parent
        member = Membership.agents.filter(quest=quest, user=user).first()
        if member:
            user_is_agent = True
    return user_is_agent


@register.filter()
def format_interval(seconds):
    hours = math.floor(seconds / 3600)
    minutes = math.floor((seconds - (hours * 3600)) / 60)
    if minutes == 0:
        return "%dч" % hours
    else:
        return "%dч %02dм" % (hours, minutes)
