from django.shortcuts import render
from coordination.models import Quest


def all_quests(request):
    quests = Quest.objects.all().order_by('-start')
    context = {'quests': quests}
    return render(request, 'coordination/quests/all.html', context)
