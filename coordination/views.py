from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from coordination.forms import QuestForm, MissionForm, HintForm
from coordination.models import Quest, Mission, Hint
from coordination.utils import is_quest_organizer, is_organizer


# Quests
def all_quests(request):
    quests = Quest.objects.all().order_by('-start')
    context = {'quests': quests}
    return render(request, 'coordination/quests/all.html', context)


def detail_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    if not quest.is_published:
        request = is_quest_organizer(request, quest)
    missions = quest.missions()
    context = {'quest': quest, 'missions': missions}
    return render(request, 'coordination/quests/detail.html', context)


@login_required()
def create_quest(request):
    request = is_organizer(request)
    if request.method == 'POST':
        form = QuestForm(request.POST)
        if form.is_valid():
            quest = form.save(commit=False)
            quest.organizer = request.user
            quest.save()
            return redirect('coordination:quest_detail', quest_id=quest.pk)
    else:
        form = QuestForm()
    context = {'form': form}
    return render(request, 'coordination/quests/form.html', context)


@login_required()
def edit_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    request = is_quest_organizer(request, quest)
    if request.method == "POST":
        form = QuestForm(request.POST, instance=quest)
        if form.is_valid():
            form.save()
            return redirect('coordination:quest_detail', quest_id=quest_id)
    else:
        form = QuestForm(instance=quest)
    context = {'form': form}
    return render(request, 'coordination/quests/form.html', context)


@login_required
def delete_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    is_quest_organizer(request, quest)
    quest.delete()
    return redirect('coordination:quests')


@login_required
def publish_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    is_quest_organizer(request, quest)
    quest.publish()
    return redirect('coordination:quest_detail', quest_id=quest_id)


# Missions
def detail_mission(request, mission_id):
    mission = get_object_or_404(Mission, pk=mission_id)
    quest = mission.quest
    if not quest.is_published or not quest.ended:
        request = is_quest_organizer(request, quest)
    hints = None
    hint_form = None
    if not mission.is_start:
        hints = mission.hints()
        if request.method == 'POST':
            hint_form = HintForm(request.POST)
            if hint_form.is_valid():
                hint = hint_form.save(commit=False)
                hint.mission = mission
                hint.save()
                return redirect('coordination:mission_detail', mission_id=mission.pk)
        else:
            hint_form = HintForm(next_number=mission.next_hint_number())
    context = {'quest': quest, 'mission': mission, 'hints': hints, 'hint_form': hint_form}
    return render(request, 'coordination/missions/detail.html', context)


@login_required()
def create_mission(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    request = is_quest_organizer(request, quest)
    if request.method == 'POST':
        form = MissionForm(request.POST)
        if form.is_valid():
            mission = form.save(commit=False)
            mission.quest = quest
            mission.save()
            return redirect('coordination:mission_detail', mission_id=mission.pk)
    else:
        form = MissionForm(next_number=quest.next_mission_number())
    context = {'quest': quest, 'form': form}
    return render(request, 'coordination/missions/form.html', context)


@login_required()
def edit_mission(request, mission_id):
    mission = get_object_or_404(Mission, pk=mission_id)
    request = is_quest_organizer(request, mission.quest)
    if request.method == "POST":
        form = MissionForm(request.POST, instance=mission)
        if form.is_valid():
            form.save()
            return redirect('coordination:mission_detail', mission_id=mission_id)
    else:
        form = MissionForm(instance=mission)
    context = {'form': form}
    return render(request, 'coordination/missions/form.html', context)


@login_required
def delete_mission(request, mission_id):
    mission = get_object_or_404(Mission, pk=mission_id)
    quest = mission.quest
    is_quest_organizer(request, quest)
    mission.delete()
    return redirect('coordination:quest_detail', quest_id=quest.pk)


# Hints
@login_required()
def edit_hint(request, hint_id):
    hint = get_object_or_404(Hint, pk=hint_id)
    request = is_quest_organizer(request, hint.mission.quest)
    if request.method == "POST":
        form = HintForm(request.POST, instance=hint)
        if form.is_valid():
            form.save()
            return redirect('coordination:mission_detail', mission_id=hint.mission.id)
    else:
        form = HintForm(instance=hint)
    context = {'form': form}
    return render(request, 'coordination/hints/form.html', context)


@login_required
def delete_hint(request, hint_id):
    hint = get_object_or_404(Hint, pk=hint_id)
    mission = hint.mission
    is_quest_organizer(request, mission.quest)
    hint.delete()
    return redirect('coordination:mission_detail', mission_id=mission.id)

