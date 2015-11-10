from django.shortcuts import render
from coordination.models import Quest


def home(request):
    coming_quests = Quest.coming_quests()[:3]
    quest = None
    if request.user.is_authenticated():
        quest = Quest.objects.filter(players=request.user).first()
    context = {'coming_quests': coming_quests, 'quest': quest}
    return render(request, 'home.html', context)
