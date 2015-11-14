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


def generate_random_username(length=8, chars=ascii_lowercase+digits):
    username = User.objects.make_random_password(length=length, allowed_chars=chars)
    try:
        User.objects.get(username=username)
        return generate_random_username(length=length, chars=chars)
    except User.DoesNotExist:
        return username


def generate_random_password(length=4, chars=digits):
    return User.objects.make_random_password(length=length, allowed_chars=chars)


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
