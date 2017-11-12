from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http.response import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from django.template.loader import render_to_string
from django.utils import timezone
from htmlmin.decorators import minified_response
from sendfile import sendfile

from coordination.forms import QuestForm, MissionForm, HintForm, PlayerForm, KeyForm, MessageForm, OrganizerForm
from coordination.models import Quest, Mission, Hint, CurrentMission, Keylog, Message, Membership
from coordination.permission_utils import is_quest_organizer, is_quest_player, is_organizer, is_organizer_features, \
    is_quest_organizer_or_agent
from coordination.utils import generate_random_username, generate_random_password, get_timedelta, is_game_over, \
    is_ml_game_over


# Quests
def all_quests(request):
    quest_list = Quest.objects.filter(parent__isnull=True).order_by('-start')
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
    quest = get_object_or_404(Quest, pk=quest_id, parent__isnull=True)
    if not quest.published:
        request = is_quest_organizer(request, quest)
    organizers = quest.organizers()
    context = {'quest': quest, 'organizers': organizers}
    return render(request, 'coordination/quests/detail.html', context)


@login_required()
def type_quest(request):
    request = is_organizer(request)
    return render(request, 'coordination/quests/type.html')


@login_required()
def create_quest(request, type=Quest.LINEAR):
    request = is_organizer(request)
    if request.method == 'POST':
        form = QuestForm(request.POST)
        if form.is_valid():
            quest = form.save(commit=False)
            quest.creator = request.user
            quest.type = type
            quest.save()
            return redirect('coordination:quest_detail', quest_id=quest.pk)
    else:
        form = QuestForm(type=type)
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
            if quest.parent:
                return redirect('coordination:line_detail', quest_id=quest.parent.id, line_id=quest.id)
            else:
                return redirect('coordination:quest_detail', quest_id=quest.id)
    else:
        form = QuestForm(instance=quest)
    context = {'form': form}
    return render(request, 'coordination/quests/form.html', context)


@login_required
def delete_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    is_quest_organizer(request, quest)
    quest.delete()
    if quest.parent:
        return redirect('coordination:quest_lines', quest_id=quest.parent.id)
    else:
        return redirect('coordination:quests')


@login_required
def publish_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id, parent__isnull=True)
    is_quest_organizer(request, quest)
    quest.publish()
    return redirect('coordination:quest_detail', quest_id=quest_id)


@minified_response
def results_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id, parent__isnull=True)
    if not quest.published:
        request = is_quest_organizer(request, quest)
    context = {'quest': quest, }
    if quest.nonlinear or quest.multilinear:
        players = quest.players_ext()
        context.update({'players': players})
    else:
        missions = quest.missions().exclude(is_finish=True)
        keylogs = Keylog.right_keylogs(missions)
        current_missions = quest.current_missions()
        context.update({'missions': missions, 'keylogs': keylogs, 'current_missions': current_missions})
    return render(request, 'coordination/quests/results.html', context)


@login_required
def tables_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id, parent__isnull=True)
    if quest.nonlinear or quest.multilinear:
        request = is_quest_organizer_or_agent(request, quest)
        rest_quest = 0
        if quest.started:
            rest_quest = get_timedelta(quest.game_over)
        players = quest.players_ext()
        missions = quest.missions_ext()
        context = {'quest': quest, 'players': players, 'missions': missions, 'rest_quest': rest_quest}
        if quest.nonlinear:
            return render(request, 'coordination/quests/tables/nonlinear.html', context)
        else:
            return render(request, 'coordination/quests/tables/multilinear.html', context)
    else:
        return redirect('coordination:quest_tables_current', quest_id=quest_id)


@login_required
@minified_response
def tables_quest_all(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id, type=Quest.LINEAR, parent__isnull=True)
    request = is_quest_organizer_or_agent(request, quest)
    players = quest.players()
    missions = quest.missions().exclude(is_finish=True)
    keylogs = Keylog.right_keylogs(missions)
    context = {'quest': quest, 'players': players, 'missions': missions, 'keylogs': keylogs}
    return render(request, 'coordination/quests/tables/all.html', context)


@login_required
@minified_response
def tables_quest_current(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id, type=Quest.LINEAR, parent__isnull=True)
    request = is_quest_organizer_or_agent(request, quest)
    current_missions = quest.current_missions()
    context = {'quest': quest, 'current_missions': current_missions}
    return render(request, 'coordination/quests/tables/current.html', context)


@login_required
def control_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id, parent__isnull=True)
    request = is_quest_organizer(request, quest)
    context = {'quest': quest, }
    if quest.nonlinear:
        rest_quest = 0
        if quest.started:
            rest_quest = get_timedelta(quest.game_over)
        context.update({'rest_quest': rest_quest})
    elif quest.linear:
        current_missions = quest.current_missions()
        context.update({'current_missions': current_missions})
    return render(request, 'coordination/quests/control.html', context)


@login_required
def begin_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id, parent__isnull=True)
    is_quest_organizer(request, quest)
    quest.begin()
    if quest.multilinear:
        players = quest.players()
        lines = quest.lines()
        for line in lines:
            first_mission = line.missions().first()
            for player in players:
                current_mission = CurrentMission.objects.filter(player=player, mission__quest=line).first()
                if not current_mission:
                    CurrentMission.objects.create(player=player, mission=first_mission)
    return redirect('coordination:quest_control', quest_id=quest_id)


@login_required
def end_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id, parent__isnull=True)
    is_quest_organizer(request, quest)
    quest.end()
    return redirect('coordination:quest_control', quest_id=quest_id)


@login_required
def clear_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id, parent__isnull=True)
    is_quest_organizer(request, quest)
    if quest.not_started:
        if quest.multilinear:
            lines = quest.lines()
            CurrentMission.objects.filter(mission__quest__in=lines).delete()
            Keylog.objects.filter(mission__quest__in=lines).delete()
        else:
            start_mission = quest.start_mission()
            CurrentMission.objects.filter(mission__quest=quest).update(mission=start_mission)
            Keylog.objects.filter(mission__quest=quest).delete()
    return redirect('coordination:quest_control', quest_id=quest_id)


@login_required
def next_mission(request, quest_id, user_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    is_quest_organizer(request, quest)
    if quest.linear and quest.started:
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
def members_quest(request, quest_id):
    return redirect('coordination:quest_players', quest_id=quest_id)


@login_required
def players_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id, parent__isnull=True)
    request = is_quest_organizer(request, quest)
    players = quest.players()
    form = PlayerForm(request.POST or None)
    if form.is_valid():
        name = form.cleaned_data["name"]
        username = generate_random_username(name)
        password = generate_random_password()
        user = User.objects.create_user(username=username, password=password, first_name=name, last_name=password)
        Membership.objects.create(quest=quest, user=user, role=Membership.PLAYER)
        if quest.linear or quest.line_nonlinear:
            start_mission = quest.start_mission()
            CurrentMission.objects.create(player=user, mission=start_mission)
        return redirect('coordination:quest_players', quest_id=quest_id)
    context = {'quest': quest, 'form': form, 'players': players}
    return render(request, 'coordination/quests/members/players.html', context)


@login_required
def players_quest_print(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id, parent__isnull=True)
    request = is_quest_organizer(request, quest)
    players = quest.players()
    context = {'quest': quest, 'players': players}
    return render(request, 'coordination/quests/members/players_print.html', context)


@login_required()
def organizers_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id, parent__isnull=True)
    request = is_quest_organizer(request, quest)
    organizers = quest.organizers()
    all_orgs = User.objects.filter(groups__name='organizers').exclude(id__in=organizers)
    if request.method == 'POST':
        form = OrganizerForm(request.POST, organizers=all_orgs)
        if form.is_valid():
            organizer = form.cleaned_data["organizer"]
            Membership.objects.create(quest=quest, user=organizer, role=Membership.ORGANIZER)
            return redirect('coordination:quest_organizers', quest_id=quest_id)
    else:
        form = OrganizerForm(organizers=all_orgs)
    agent = quest.agents().first()
    context = {'quest': quest, 'organizers': organizers, 'form': form, 'agent': agent}
    return render(request, 'coordination/quests/members/organizers.html', context)


@login_required
def delete_organizer(request, quest_id, user_id):
    quest = get_object_or_404(Quest, pk=quest_id, parent__isnull=True)
    is_quest_organizer(request, quest)
    user = get_object_or_404(User, pk=user_id)
    if quest.creator != user or request.user != user:
        member = get_object_or_404(Membership, quest=quest, user=user)
        if member.organizer:
            member.delete()
    return redirect('coordination:quest_organizers', quest_id=quest_id)


@login_required
def delete_player(request, quest_id, user_id):
    quest = get_object_or_404(Quest, pk=quest_id, parent__isnull=True)
    is_quest_organizer(request, quest)
    user = get_object_or_404(User, pk=user_id)
    member = get_object_or_404(Membership, quest=quest, user=user)
    if member.player:
        user.delete()
    return redirect('coordination:quest_players', quest_id=quest_id)


@login_required
def delete_players(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id, parent__isnull=True)
    is_quest_organizer(request, quest)
    player_ids = request.POST.getlist('delete_ids[]')
    users = User.objects.filter(id__in=player_ids)
    for user in users:
        member = Membership.players.filter(quest=quest, user=user).first()
        if member and member.player:
            user.delete()
    return redirect('coordination:quest_players', quest_id=quest_id)


@login_required
def coordination_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id, parent__isnull=True)
    request = is_quest_player(request, quest)
    if quest.nonlinear:
        return nonlinear_coordination(request, quest)
    elif quest.multilinear:
        return multilinear_coordination(request, quest)
    else:
        return linear_coordination(request, quest)


def nonlinear_coordination(request, quest):
    player = request.user
    if request.method == 'POST':
        mission = get_object_or_404(Mission, pk=request.POST['mission_id'])
        if quest.started and not quest.is_game_over and not mission.is_completed(player):
            form = KeyForm(request.POST, quest=quest)
            if form.is_valid():
                key = form.cleaned_data["key"]
                right_key = mission.key
                is_right = len(right_key) > 0 and right_key == key
                keylog = Keylog(key=key, fix_time=timezone.now(), player=player,
                                mission=mission, is_right=is_right)
                if is_right:
                    keylog.points = mission.points
                keylog.save()
        if mission.order_number > 1:
            url = '{0}#m{1}'.format(resolve_url('coordination:quest_coordination', quest_id=quest.id),
                                    mission.order_number - 1)
        else:
            url = resolve_url('coordination:quest_coordination', quest_id=quest.id)
        return redirect(url)
    else:
        rest_quest = None
        missions = None
        mission_start = None
        mission_finish = None
        display_hints = None
        rest_hints = None
        form = None
        if quest.not_started:
            mission_start = quest.start_mission()
        else:
            if quest.started and not quest.is_game_over:
                rest_quest = get_timedelta(quest.game_over)
            form = KeyForm(quest=quest)
            count = 0
            missions = quest.missions().filter(order_number__gt=0, is_finish=False)
            for mission in missions:
                mission.wrong_keys = Keylog.wrong_keylogs_format(player, mission)
                is_completed = mission.is_completed(player)
                mission.is_completed = is_completed
                if not is_completed:
                    count += 1
            if is_game_over(count, missions, quest):
                mission_finish = quest.finish_mission()
            display_hints, rest_hints = Mission.hints_in_nl(quest, missions)
        points = Keylog.total_points(quest, player)
        messages = quest.messages().filter(is_show=True)
        context = {'quest': quest, 'messages': messages, 'missions': missions, 'mission_finish': mission_finish,
                   'mission_start': mission_start, 'rest_quest': rest_quest, 'points': points, 'form': form,
                   'display_hints': display_hints, 'rest_hints': rest_hints}
        return render(request, 'coordination/quests/coordination/nonlinear.html', context)


def linear_coordination(request, quest):
    player = request.user
    current_mission = get_object_or_404(CurrentMission, mission__quest=quest, player=player)
    mission = current_mission.mission
    if request.method == 'POST':
        if quest.started and not mission.is_finish:
            form = KeyForm(request.POST, quest=quest)
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
                keylog = Keylog(key=key, fix_time=timezone.now(), player=player, mission=mission, is_right=is_right)
                keylog.save()
                if is_right:
                    current_mission.mission = next_mission
                    current_mission.start_time = keylog.fix_time
                    current_mission.save()
        return redirect('coordination:quest_coordination', quest_id=quest.id)
    else:
        hints = current_mission.display_hints()
        next_hint_time = current_mission.next_hint_time()
        delay = get_timedelta(next_hint_time) if next_hint_time else None
        completed_missions = Mission.completed_missions(quest, player)
        form = None
        wrong_keys = None
        messages = quest.messages().filter(is_show=True)
        if quest.started and not mission.is_finish:
            form = KeyForm(quest=quest)
            wrong_keys = Keylog.wrong_keylogs_format(player, mission)
        context = {'quest': quest, 'mission': mission, 'hints': hints, 'form': form, 'messages': messages,
                   'wrong_keys': wrong_keys, 'delay': delay, 'completed_missions': completed_missions}
        return render(request, 'coordination/quests/coordination/general.html', context)


def multilinear_coordination(request, quest):
    player = request.user
    if request.method == 'POST':
        mission = get_object_or_404(Mission, pk=request.POST['mission_id'])
        line = mission.quest
        if quest.started and not quest.is_game_over and not mission.is_completed(player):
            form = KeyForm(request.POST, quest=quest)
            if form.is_valid():
                key = form.cleaned_data["key"]
                right_key = mission.key
                is_right = len(right_key) > 0 and right_key == key
                keylog = Keylog(key=key, fix_time=timezone.now(), player=player, mission=mission, is_right=is_right)
                if is_right:
                    keylog.points = mission.points
                    next_mission = Mission.objects.filter(quest=line, order_number=mission.order_number + 1).first()
                    current_mission = get_object_or_404(CurrentMission, mission__quest=line, player=player)
                    current_mission.mission = next_mission
                    current_mission.start_time = keylog.fix_time
                    current_mission.save()
                keylog.save()
        url = '{0}#l{1}'.format(resolve_url('coordination:quest_coordination', quest_id=quest.id), line.id)
        return redirect(url)
    else:
        rest_quest = None
        lines = None
        mission_start = None
        mission_finish = None
        form = None
        if quest.not_started:
            mission_start = quest.start_mission()
        else:
            game_over = is_ml_game_over(player, quest)
            if game_over:
                mission_finish = quest.finish_mission()

            if quest.started and not quest.is_game_over:
                rest_quest = get_timedelta(quest.game_over)
                form = KeyForm(quest=quest)
            lines = quest.lines()
            for line in lines:
                line.completed_missions = Mission.completed_missions(line, player)
                if game_over:
                    all_missions = line.missions().filter(order_number__gt=0, is_finish=False)
                    line.uncompleted_missions = [i for i in all_missions if i not in line.completed_missions]
                else:
                    current_mission = get_object_or_404(CurrentMission, mission__quest=line, player=player)
                    line.mission = current_mission.mission
                    line.hints = current_mission.display_hints()
                    line.next_hint_time = current_mission.next_hint_time()
                    line.wrong_keys = Keylog.wrong_keylogs_format(player, line.mission)

        points = Keylog.total_points(quest, player)
        messages = quest.messages().filter(is_show=True)
        context = {'quest': quest, 'messages': messages, 'lines': lines, 'mission_finish': mission_finish,
                   'mission_start': mission_start, 'rest_quest': rest_quest, 'points': points, 'form': form}
        return render(request, 'coordination/quests/coordination/multilinear.html', context)


@login_required
def coordination_quest_ajax(request, quest_id):
    if request.is_ajax():
        quest = get_object_or_404(Quest, pk=quest_id, parent__isnull=True)
        request = is_quest_player(request, quest)
        player = request.user
        messages = quest.messages().filter(is_show=True)
        html_messages = render_to_string('coordination/messages/_list.html', {'messages': messages})
        data = {'messages': html_messages, }
        if quest.nonlinear or quest.multilinear:
            rest_quest = None
            if quest.started and not quest.is_game_over:
                rest_quest = get_timedelta(quest.game_over)
            count = 0
            missions = quest.missions().filter(order_number__gt=0, is_finish=False)
            for mission in missions:
                is_completed = mission.is_completed(request.user)
                if not is_completed:
                    count += 1
            mission_finish = None
            if missions and count == 0 or quest.is_game_over or quest.ended:
                mission_finish = quest.finish_mission()
            html_mission_finish = render_to_string('coordination/quests/coordination/_mission_finish.html',
                                                   {'mission_finish': mission_finish})
            data.update({'rest_quest': rest_quest, 'mission_finish': html_mission_finish})
        else:
            current_mission = get_object_or_404(CurrentMission, mission__quest=quest, player=player)
            mission = current_mission.mission
            hints = current_mission.display_hints()
            next_hint_time = current_mission.next_hint_time()
            delay = None
            if next_hint_time:
                delay = get_timedelta(next_hint_time)
            completed_missions = Mission.completed_missions(quest, player)

            wrong_keys_str = None
            if quest.started and not mission.is_finish:
                wrong_keys_str = Keylog.wrong_keylogs_format(player, mission)
            json_mission = mission.as_json()
            html_picture = render_to_string('coordination/quests/coordination/_picture.html', {'mission': mission})
            html_hints = render_to_string('coordination/hints/_list.html', {'hints': hints})
            html_wrong_keys = render_to_string('coordination/quests/coordination/_wrong_keys.html',
                                               {'wrong_keys': wrong_keys_str})
            html_completed_missions = render_to_string('coordination/quests/coordination/_completed_missions.html',
                                                       {'completed_missions': completed_missions})
            hide_form = not quest.started or mission.is_finish
            data.update({'mission': json_mission, 'hints': html_hints, 'delay': delay, 'wrong_keys': html_wrong_keys,
                         'completed_missions': html_completed_missions, 'hide_form': hide_form,
                         'picture': html_picture})
        return JsonResponse(data)
    else:
        raise Http404


@login_required
@minified_response
def keylog_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id, parent__isnull=True)
    request = is_quest_organizer(request, quest)
    mission = request.GET.get('mission', None)
    player = request.GET.get('player', None)
    missions = quest.missions().exclude(is_finish=True)
    if quest.nonlinear or quest.multilinear:
        missions = missions.exclude(order_number=0)
    if not mission and not player:
        url = reverse('coordination:quest_keylog', args=[quest.id])
        return redirect('{0}?mission={1}'.format(url, missions.first().id))
    keylogs = None
    players = quest.players()
    if mission:
        keylogs = Keylog.objects.filter(mission__id=mission)
        mission = int(mission)
    if player:
        keylogs = Keylog.objects.filter(player__id=player)
        player = int(player)
    context = {'quest': quest, 'keylogs': keylogs, 'players': players, 'missions': missions,
               'cur_mission': mission, 'cur_player': player}
    return render(request, 'coordination/quests/keylog.html', context)


@login_required
def delete_keylog(request, quest_id, keylog_id):
    quest = get_object_or_404(Quest, pk=quest_id, parent__isnull=True)
    is_quest_organizer(request, quest)
    keylog = get_object_or_404(Keylog, pk=keylog_id, mission__quest=quest)
    keylog.delete()
    return redirect('coordination:quest_keylog', quest_id=quest_id)


@login_required
def delete_keylogs(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id, parent__isnull=True)
    is_quest_organizer(request, quest)
    keylog_ids = request.POST.getlist('delete_ids[]')
    Keylog.objects.filter(mission__quest=quest, id__in=keylog_ids).delete()
    return redirect('coordination:quest_keylog', quest_id=quest_id)


@login_required
def messages_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id, parent__isnull=True)
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
    quest = get_object_or_404(Quest, pk=quest_id, parent__isnull=True)
    is_quest_organizer(request, quest)
    message = get_object_or_404(Message, pk=message_id, quest=quest)
    message.show()
    return redirect('coordination:quest_messages', quest_id=quest_id)


@login_required()
def edit_message(request, quest_id, message_id):
    quest = get_object_or_404(Quest, pk=quest_id, parent__isnull=True)
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
def delete_message(request, quest_id, message_id, parent__isnull=True):
    quest = get_object_or_404(Quest, pk=quest_id)
    is_quest_organizer(request, quest)
    message = get_object_or_404(Message, pk=message_id, quest=quest)
    message.delete()
    return redirect('coordination:quest_messages', quest_id=quest_id)


# Missions
@login_required()
def create_line(request, quest_id, type=Quest.LINEAR):
    quest = get_object_or_404(Quest, pk=quest_id, type=Quest.MULTILINEAR)
    request = is_quest_organizer(request, quest)
    if request.method == 'POST':
        form = QuestForm(request.POST)
        if form.is_valid():
            line = form.save(commit=False)
            line.creator = quest.creator
            line.type = type
            line.parent = quest
            line.save()
            return redirect('coordination:line_detail', quest_id=quest.id, line_id=line.pk)
    else:
        form = QuestForm(type=type, parent=quest)
    context = {'form': form}
    return render(request, 'coordination/quests/form.html', context)


def detail_line(request, quest_id, line_id):
    quest = get_object_or_404(Quest, pk=quest_id, type=Quest.MULTILINEAR)
    if not quest.published:
        request = is_quest_organizer(request, quest)
    line = get_object_or_404(Quest, pk=line_id, parent=quest)
    missions = line.missions()
    context = {'quest': quest, 'line': line, 'missions': missions}
    return render(request, 'coordination/missions/line_detail.html', context)


def quest_lines(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id, type=Quest.MULTILINEAR)
    if not quest.published:
        request = is_quest_organizer_or_agent(request, quest)
    mission_start = quest.start_mission()
    mission_finish = quest.finish_mission()
    lines = quest.lines()
    context = {'quest': quest, 'mission_start': mission_start, 'mission_finish': mission_finish, 'lines': lines}
    return render(request, 'coordination/missions/lines.html', context)


def quest_missions(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id, parent__isnull=True)
    if not quest.published:
        request = is_quest_organizer_or_agent(request, quest)
    if quest.multilinear:
        return redirect('coordination:quest_lines', quest_id=quest.id)
    missions = quest.missions()
    context = {'quest': quest, 'missions': missions}
    return render(request, 'coordination/missions/all.html', context)


def detail_mission(request, mission_id):
    mission = get_object_or_404(Mission, pk=mission_id)
    quest = mission.quest
    user = request.user
    can_user_view = quest.published and \
                    (quest.ended or quest.is_game_over or (user.is_authenticated() and mission.is_completed(user)))
    if not can_user_view:
        request = is_quest_organizer_or_agent(request, quest)
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
    if quest.not_started:
        request = is_quest_organizer(request, quest)
        if request.method == 'POST':
            form = MissionForm(request.POST, request.FILES, quest=quest)
            if form.is_valid():
                mission = form.save(commit=False)
                mission.quest = quest
                mission.save()
                return redirect('coordination:mission_detail', mission_id=mission.pk)
        else:
            form = MissionForm(quest=quest)
        context = {'quest': quest, 'form': form}
        return render(request, 'coordination/missions/form.html', context)
    if quest.parent:
        return redirect('coordination:quest_lines', quest_id=quest.pk)
    else:
        return redirect('coordination:quest_missions', quest_id=quest.pk)


@login_required()
def create_finish_mission(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id, type=Quest.LINE_NONLINEAR)
    if quest.not_started:
        is_quest_organizer(request, quest)
        finish = Mission.objects.create(quest=quest, name_in_table='Финиш', order_number=1, is_finish=True)
        Mission.update_finish_number(quest)
        return redirect('coordination:mission_detail', mission_id=finish.id)
    return redirect('coordination:quest_missions', quest_id=quest.pk)


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
    if not quest.started:
        is_quest_organizer(request, quest)
        if quest.linear or quest.nonlinear:
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
        can_user_view = quest.published and \
                        (quest.ended or (player.is_authenticated() and mission.is_completed(player))
                         or (player.is_authenticated() and mission.is_current(player)))
        if not can_user_view:
            request = is_quest_organizer_or_agent(request, quest)
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
