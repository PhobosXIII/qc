from random import choice
from string import ascii_lowercase, digits
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.utils import timezone


def is_organizer(request):
    if bool(request.user.groups.filter(name='organizers').values('name')):
        return request
    raise PermissionDenied


def is_quest_organizer(request, quest):
    if request.user == quest.organizer or request.user.is_superuser:
        return request
    raise PermissionDenied


def is_quest_player(request, quest):
    if request.user in quest.players.all():
        return request
    raise PermissionDenied


def generate_random_username(length=6, chars=ascii_lowercase+digits, split=3, delimiter='-'):
    username = ''.join([choice(chars) for i in range(length)])
    if split:
        username = delimiter.join([username[start:start+split] for start in range(0, len(username), split)])
    try:
        User.objects.get(username=username)
        return generate_random_username(length=length, chars=chars, split=split, delimiter=delimiter)
    except User.DoesNotExist:
        return username


def get_timedelta(time):
    now = timezone.now()
    if time < now:
        return 0
    timedelta = time - now
    return timedelta.seconds


def get_timedelta_with_now(time):
    now = timezone.now()
    if now < time:
        return 0
    timedelta = now - time
    return timedelta.seconds


def time_in_minutes(time):
    return time // 60
