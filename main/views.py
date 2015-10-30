from django.shortcuts import render
from coordination.models import Quest


def home(request):
    coming_quests = Quest.coming_quests()[:3]
    context = {'coming_quests': coming_quests}
    return render(request, 'home.html', context)
