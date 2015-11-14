from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from coordination.forms import QuestForm, MissionForm, HintForm, PlayerForm, KeyForm, MessageForm
from coordination.models import Quest, Mission, Hint, CurrentMission, Keylog, Message
from coordination.utils import is_quest_organizer, is_quest_player, is_organizer, generate_random_username, \
    generate_random_password


# Quests
def all_quests(request):
    quest_list = Quest.objects.all().order_by('-start')
    paginator = Paginator(quest_list, 15)
    page = request.GET.get('page')
    try:
        quests = paginator.page(page)
    except PageNotAnInteger:
        quests = paginator.page(1)
    except EmptyPage:
        quests = paginator.page(paginator.num_pages)
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


def results_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    missions = quest.missions().exclude(is_finish=True)
    keylogs = Keylog.right_keylogs(missions)
    current_missions = quest.current_missions()
    context = {'quest': quest, 'missions': missions, 'keylogs': keylogs, 'current_missions': current_missions}
    return render(request, 'coordination/quests/results.html', context)


@login_required
def tables_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    is_quest_organizer(request, quest)
    players = quest.players.all().order_by('first_name')
    missions = quest.missions().exclude(is_finish=True)
    keylogs = Keylog.right_keylogs(missions)
    current_missions = quest.current_missions()
    context = {'quest': quest, 'players': players, 'missions': missions, 'keylogs': keylogs,
               'current_missions': current_missions, }
    return render(request, 'coordination/quests/tables.html', context)


@login_required
def control_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    is_quest_organizer(request, quest)
    current_missions = quest.current_missions()
    context = {'quest': quest, 'current_missions': current_missions}
    return render(request, 'coordination/quests/control.html', context)


@login_required
def begin_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    is_quest_organizer(request, quest)
    quest.begin()
    return redirect('coordination:quest_control', quest_id=quest_id)


@login_required
def end_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    is_quest_organizer(request, quest)
    quest.end()
    return redirect('coordination:quest_control', quest_id=quest_id)


@login_required
def clear_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    is_quest_organizer(request, quest)
    if quest.not_started:
        start_mission = quest.start_mission()
        CurrentMission.objects.filter(mission__quest=quest).update(mission=start_mission)
        Keylog.objects.filter(mission__quest=quest).delete()
    return redirect('coordination:quest_control', quest_id=quest_id)


@login_required
def next_mission(request, quest_id, user_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    is_quest_organizer(request, quest)
    if quest.started:
        player = get_object_or_404(User, pk=user_id)
        cm = get_object_or_404(CurrentMission, mission__quest=quest, player=player)
        if not cm.mission.is_finish:
            right_key = cm.mission.key
            keylog = Keylog(key=right_key, fix_time=timezone.now(), player=player, mission=cm.mission, is_right=True)
            cm.mission = Mission.objects.get(order_number=cm.mission.order_number + 1)
            cm.start_time = keylog.fix_time
            keylog.save()
            cm.save()
    return redirect('coordination:quest_control', quest_id=quest_id)


@login_required
def players_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    is_quest_organizer(request, quest)
    players = quest.players.all().order_by('first_name')
    form = PlayerForm(request.POST or None)
    if form.is_valid():
        name = form.cleaned_data["name"]
        username = generate_random_username()
        password = generate_random_password()
        user = User.objects.create_user(username=username, password=password, first_name=name, last_name=password)
        quest.players.add(user)
        start_mission = quest.start_mission()
        CurrentMission.objects.create(player=user, mission=start_mission)
        return redirect('coordination:quest_players', quest_id=quest_id)
    context = {'quest': quest, 'form': form, 'players': players}
    return render(request, 'coordination/quests/players.html', context)


@login_required
def delete_player(request, quest_id, player_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    is_quest_organizer(request, quest)
    player = get_object_or_404(User, pk=player_id)
    quest.players.remove(player)
    player.delete()
    return redirect('coordination:quest_players', quest_id=quest_id)


@login_required
def coordination_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    request = is_quest_player(request, quest)
    player = request.user
    current_mission = get_object_or_404(CurrentMission, mission__quest=quest, player=player)
    mission = current_mission.mission
    hints = Hint.display_hints(current_mission)
    next_hint_time = Hint.next_hint_time(current_mission)
    completed_missions = Mission.completed_missions(quest, player)
    messages = quest.messages().filter(is_show=True)
    form = None
    wrong_keys_str = None
    if not mission.is_finish and quest.started:
        form = KeyForm(request.POST or None)
        if form.is_valid():
            key = form.cleaned_data["key"].strip()
            right_key = mission.key.strip()
            keylog = Keylog(key=key, fix_time=timezone.now(), player=player, mission=mission)
            if right_key == key:
                keylog.is_right = True
                current_mission.mission = Mission.objects.get(quest=quest, order_number=mission.order_number + 1)
                current_mission.start_time = keylog.fix_time
            keylog.save()
            current_mission.save()
            return redirect('coordination:quest_coordination', quest_id=quest_id)
        wrong_keys = Keylog.wrong_keylogs(player, mission)
        wrong_keys_str = ', '.join(str(i) for i in wrong_keys)
    context = {'quest': quest, 'mission': mission, 'hints': hints, 'form': form, 'wrong_keys': wrong_keys_str,
               'next_hint_time': next_hint_time, 'completed_missions': completed_missions, 'messages': messages}
    return render(request, 'coordination/quests/coordination.html', context)


@login_required
def keylog_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    request = is_quest_organizer(request, quest)
    keylog_list = Keylog.objects.filter(mission__quest=quest).order_by('mission', 'player', 'fix_time')
    paginator = Paginator(keylog_list, 30)
    page = request.GET.get('page')
    try:
        keylogs = paginator.page(page)
    except PageNotAnInteger:
        keylogs = paginator.page(1)
    except EmptyPage:
        keylogs = paginator.page(paginator.num_pages)
    context = {'quest': quest, 'keylogs': keylogs}
    return render(request, 'coordination/quests/keylog.html', context)


@login_required
def delete_keylog(request, quest_id, keylog_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    is_quest_organizer(request, quest)
    keylog = get_object_or_404(Keylog, pk=keylog_id)
    keylog.delete()
    return redirect('coordination:quest_keylog', quest_id=quest_id)


def messages_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    request = is_quest_organizer(request, quest)
    messages = quest.messages()
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.quest = quest
            message.save()
            return redirect('coordination:quest_messages', quest_id=quest.id)
    else:
        form = MessageForm()
    context = {'quest': quest, 'messages': messages, 'form': form}
    return render(request, 'coordination/quests/messages.html', context)


@login_required
def show_message(request, quest_id, message_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    is_quest_organizer(request, quest)
    message = get_object_or_404(Message, pk=message_id)
    message.show()
    return redirect('coordination:quest_messages', quest_id=quest_id)


@login_required()
def edit_message(request, quest_id, message_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    request = is_quest_organizer(request, quest)
    message = get_object_or_404(Message, pk=message_id)
    if request.method == "POST":
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            return redirect('coordination:quest_messages', quest_id=quest_id)
    else:
        form = MessageForm(instance=message)
    context = {'form': form}
    return render(request, 'coordination/messages/form.html', context)


@login_required
def delete_message(request, quest_id, message_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    is_quest_organizer(request, quest)
    message = get_object_or_404(Message, pk=message_id)
    message.delete()
    return redirect('coordination:quest_messages', quest_id=quest_id)


# Missions
def detail_mission(request, mission_id):
    mission = get_object_or_404(Mission, pk=mission_id)
    quest = mission.quest
    can_user_view = quest.is_published and \
                    (quest.ended or (request.user.is_authenticated() and mission.is_completed(request.user)))
    if not can_user_view:
        request = is_quest_organizer(request, quest)
    hints = None
    hint_form = None
    if not mission.is_start and not mission.is_finish:
        hints = mission.hints()
        if request.method == 'POST':
            hint_form = HintForm(request.POST)
            if hint_form.is_valid():
                hint = hint_form.save(commit=False)
                hint.mission = mission
                hint.save()
                return redirect('coordination:mission_detail', mission_id=mission.id)
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
    if not mission.is_start and not mission.is_finish:
        mission.delete()
        Mission.update_finish_number(quest)
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
