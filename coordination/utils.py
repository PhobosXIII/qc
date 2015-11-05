from random import choice
from string import ascii_lowercase, digits
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User


def is_organizer(request):
    if bool(request.user.groups.filter(name='organizers').values('name')):
        return request
    raise PermissionDenied


def is_quest_organizer(request, quest):
    if request.user == quest.organizer or request.user.is_superuser:
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