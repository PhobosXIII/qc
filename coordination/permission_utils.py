from django.core.exceptions import PermissionDenied


def is_organizer(request):
    if bool(request.user.groups.filter(name='organizers').values('name')):
        return request
    raise PermissionDenied


def is_organizer_features(request):
    if bool(request.user.groups.filter(name='organizers_features').values('name')):
        return request
    raise PermissionDenied


def is_quest_organizer(request, quest):
    member = quest.membership_set.filter(user=request.user).first()
    if (member and member.organizer) or request.user.is_superuser:
        return request
    raise PermissionDenied


def is_quest_player(request, quest):
    member = quest.membership_set.filter(user=request.user).first()
    if quest.is_published and member and member.player:
        return request
    raise PermissionDenied
