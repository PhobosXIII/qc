from django.core.exceptions import PermissionDenied


def is_organizer(request):
    if bool(request.user.groups.filter(name='organizers').values('name')):
        return request
    raise PermissionDenied


def is_quest_organizer(request, quest):
    if request.user == quest.organizer or request.user.is_superuser:
        return request
    raise PermissionDenied
