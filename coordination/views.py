from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http.response import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from sendfile import sendfile

from coordination.forms import QuestForm, MissionForm, HintForm, PlayerForm, KeyForm, MessageForm
from coordination.models import Quest, Mission, Hint, CurrentMission, Keylog, Message
from coordination.utils import is_quest_organizer, is_quest_player, is_organizer, generate_random_username, \
    generate_random_password, is_organizer_features, get_timedelta


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
    context = {'quest': quest}
    return render(request, 'coordination/quests/detail.html', context)


@login_required()
def create_quest(request, type='L'):
    if type != 'L':
        request = is_organizer_features(request)
    request = is_organizer(request)
    if request.method == 'POST':
        form = QuestForm(request.POST)
        if form.is_valid():
            quest = form.save(commit=False)
            quest.organizer = request.user
            quest.type = type
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
    return redirect('coordination:quest_tables_current', quest_id=quest_id)


@login_required
def tables_quest_all(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    is_quest_organizer(request, quest)
    players = quest.players.all().order_by('first_name')
    missions = quest.missions().exclude(is_finish=True)
    keylogs = Keylog.right_keylogs(missions)
    context = {'quest': quest, 'players': players, 'missions': missions, 'keylogs': keylogs}
    return render(request, 'coordination/quests/tables/all.html', context)


@login_required
def tables_quest_current(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    is_quest_organizer(request, quest)
    current_missions = quest.current_missions()
    context = {'quest': quest, 'current_missions': current_missions}
    return render(request, 'coordination/quests/tables/current.html', context)


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
            cm.mission = Mission.objects.get(quest=quest, order_number=cm.mission.order_number + 1)
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
        username = generate_random_username(name)
        password = generate_random_password()
        user = User.objects.create_user(username=username, password=password, first_name=name, last_name=password)
        quest.players.add(user)
        start_mission = quest.start_mission()
        CurrentMission.objects.create(player=user, mission=start_mission)
        return redirect('coordination:quest_players', quest_id=quest_id)
    context = {'quest': quest, 'form': form, 'players': players}
    return render(request, 'coordination/quests/players.html', context)


@login_required
def players_quest_print(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    is_quest_organizer(request, quest)
    players = quest.players.all().order_by('first_name')
    context = {'quest': quest, 'players': players}
    return render(request, 'coordination/quests/players_print.html', context)


@login_required
def delete_player(request, quest_id, player_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    is_quest_organizer(request, quest)
    player = get_object_or_404(User, pk=player_id)
    quest.players.remove(player)
    player.delete()
    return redirect('coordination:quest_players', quest_id=quest_id)


@login_required
def delete_players(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    is_quest_organizer(request, quest)
    player_ids = request.POST.getlist('delete_ids[]')
    User.objects.filter(id__in=player_ids).delete()
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
    delay = None
    if next_hint_time:
        delay = get_timedelta(next_hint_time)
    completed_missions = Mission.completed_missions(quest, player)
    messages = quest.messages().filter(is_show=True)
    form = None
    wrong_keys_str = None
    if quest.started and not mission.is_finish:
        form = KeyForm(request.POST or None)
        if form.is_valid():
            key = form.cleaned_data["key"]
            next_missions = Mission.objects.filter(quest=quest, order_number=mission.order_number + 1)
            if quest.linear:
                right_key = mission.key
                next_mission = next_missions.first()
                is_right = len(right_key) > 0 and right_key == key
            else:
                next_mission = next_missions.filter(key=key).first()
                is_right = next_mission is not None
            keylog = Keylog(key=key, fix_time=timezone.now(), player=player, mission=mission)
            if is_right:
                keylog.is_right = True
                current_mission.mission = next_mission
                current_mission.start_time = keylog.fix_time
                current_mission.save()
            keylog.save()
        wrong_keys = Keylog.wrong_keylogs(player, mission)
        wrong_keys_str = ', '.join(str(i) for i in wrong_keys)
    if request.method == 'GET':
        if request.is_ajax():
            json_mission = mission.as_json()
            html_hints = render_to_string('coordination/hints/_list.html', {'hints': hints})
            html_messages = render_to_string('coordination/messages/_list.html', {'messages': messages})
            html_wrong_keys = render_to_string('coordination/quests/_wrong_keys.html',
                                               {'wrong_keys': wrong_keys_str})
            html_completed_missions = render_to_string('coordination/quests/_completed_missions.html',
                                                       {'completed_missions': completed_missions})
            hide_form = form is None
            data = {'mission': json_mission, 'hints': html_hints, 'delay': delay, 'messages': html_messages,
                    'wrong_keys': html_wrong_keys, 'completed_missions': html_completed_missions,
                    'hide_form': hide_form}
            return JsonResponse(data)
        else:
            context = {'quest': quest, 'mission': mission, 'hints': hints, 'form': form,
                       'wrong_keys': wrong_keys_str, 'delay': delay, 'completed_missions': completed_missions,
                       'messages': messages}
            return render(request, 'coordination/quests/coordination.html', context)
    if request.method == 'POST':
        return redirect('coordination:quest_coordination', quest_id=quest_id)


@login_required
def keylog_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    request = is_quest_organizer(request, quest)
    keylog_list = Keylog.objects.filter(mission__quest=quest).order_by('mission', 'player', 'fix_time')
    paginator = Paginator(keylog_list, 60)
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


@login_required
def delete_keylogs(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    is_quest_organizer(request, quest)
    keylog_ids = request.POST.getlist('delete_ids[]')
    Keylog.objects.filter(id__in=keylog_ids).delete()
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
def quest_missions(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    if not quest.is_published or not quest.ended:
        request = is_quest_organizer(request, quest)
    missions = quest.missions()
    context = {'quest': quest, 'missions': missions}
    return render(request, 'coordination/missions/all.html', context)


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
        form = MissionForm(request.POST, request.FILES)
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
def create_finish_mission(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    is_quest_organizer(request, quest)
    finish = Mission.objects.create(quest=quest, name_in_table='Финиш', order_number=1, is_finish=True)
    Mission.update_finish_number(quest)
    return redirect('coordination:mission_detail', mission_id=finish.id)


@login_required()
def edit_mission(request, mission_id):
    mission = get_object_or_404(Mission, pk=mission_id)
    request = is_quest_organizer(request, mission.quest)
    if request.method == "POST":
        form = MissionForm(request.POST, request.FILES, instance=mission)
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
    if quest.linear:
        if not mission.is_start and not mission.is_finish:
            mission.delete()
            Mission.update_finish_number(quest)
    else:
        if not mission.is_start:
            mission.delete()
            Mission.update_finish_number(quest)
    return redirect('coordination:quest_missions', quest_id=quest.pk)


def picture_mission(request, mission_id):
    mission = get_object_or_404(Mission, pk=mission_id)
    if mission.picture:
        quest = mission.quest
        player = request.user
        can_user_view = quest.is_published and \
                        (quest.ended or (player.is_authenticated() and mission.is_completed(player))
                         or (player.is_authenticated() and mission.is_current(player)))
        if not can_user_view:
            request = is_quest_organizer(request, quest)
        return sendfile(request, mission.picture.path)
    else:
        raise Http404


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
