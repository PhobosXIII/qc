from django.shortcuts import render, get_object_or_404
from coordination.forms import QuestForm
from coordination.models import Quest


def all_quests(request):
    quests = Quest.objects.all().order_by('-start')
    context = {'quests': quests}
    return render(request, 'coordination/quests/all.html', context)


def create_quest(request):
    form = QuestForm(request.POST or None)
    context = {'form': form}


def detail_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    context = {'quest': quest}
    return render(request, 'coordination/quests/detail.html', context)

