from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from coordination.models import Quest
from coordination.utils import is_organizer


def home(request):
    coming_quests = Quest.coming_quests()[:3]
    quest = None
    if request.user.is_authenticated():
        quest = Quest.objects.filter(players=request.user).first()
    context = {'coming_quests': coming_quests, 'quest': quest}
    return render(request, 'home.html', context)


def my_profile(request):
    request = is_organizer(request)
    quest_list = Quest.my_quests(request.user)
    paginator = Paginator(quest_list, 10)
    page = request.GET.get('page')
    try:
        my_quests = paginator.page(page)
    except PageNotAnInteger:
        my_quests = paginator.page(1)
    except EmptyPage:
        my_quests = paginator.page(paginator.num_pages)
    context = {'my_quests': my_quests}
    return render(request, 'registration/my_profile.html', context)
