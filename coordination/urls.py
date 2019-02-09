from django.conf.urls import include
from django.urls import path, re_path

from coordination.models import Quest
from . import views

quest_patterns = [
    path('quests/', views.all_quests, name='quests'),
    path('quests/new/', include([
        path('l/', views.create_quest, {'type': Quest.LINEAR}, name='quest_new_l'),
        path('nl/', views.create_quest, {'type': Quest.NONLINEAR}, name='quest_new_nl'),
        # TODO MC: 02.01.2019 uncomment when re-implement LNL quest
        # path('lnl/', views.create_quest, {'type': Quest.LINE_NONLINEAR}, name='quest_new_lnl'),
        path('ml/', views.create_quest, {'type': Quest.MULTILINEAR}, name='quest_new_ml'),
        path('type/', views.type_quest, name='quest_new_type'),
    ])),
    path('quests/<int:quest_id>/', include([
        path('', views.detail_quest, name='quest_detail'),
        path('edit/', views.edit_quest, name='quest_edit'),
        path('delete/', views.delete_quest, name='quest_delete'),
        path('publish/', views.publish_quest, name='quest_publish'),
        path('missions/', include([
            path('', views.quest_missions, name='quest_missions'),
            path('lines/', views.quest_lines, name='quest_lines'),
            path('lines/new/', views.create_line, name='line_new'),
            path('lines/<int:line_id>/', views.detail_line, name='line_detail'),
        ])),
        path('control/', include([
            path('', views.control_quest, name='quest_control'),
            path('begin/', views.begin_quest, name='begin_quest'),
            path('end/', views.end_quest, name='end_quest'),
            path('clear/', views.clear_quest, name='clear_quest'),
            path('next_mission/<int:user_id>/', views.next_mission, name='next_mission'),
        ])),
        path('members/', include([
            path('', views.members_quest, name='quest_members'),
            path('players/', include([
                path('', views.players_quest, name='quest_players'),
                path('print/', views.players_quest_print, name='quest_players_print'),
                path('delete/', views.delete_players, name='players_delete'),
                path('delete/<int:user_id>/', views.delete_player, name='player_delete'),
            ])),
            path('organizers/', include([
                path('', views.organizers_quest, name='quest_organizers'),
                path('delete/<int:user_id>/', views.delete_organizer, name='organizer_delete'),
            ])),
        ])),
        path('coordination/', views.coordination_quest, name='quest_coordination'),
        path('coordination_ajax/', views.coordination_quest_ajax, name='quest_coordination_ajax'),
        path('tables/', include([
            path('', views.tables_quest, name='quest_tables'),
            path('current/', views.tables_quest_current, name='quest_tables_current'),
            path('all/', views.tables_quest_all, name='quest_tables_all'),
        ])),
        path('results/', views.results_quest, name='quest_results'),
        path('key_log/', include([
            path('', views.key_log_quest, name='quest_key_log'),
            path('delete/', views.delete_key_logs, name='key_logs_delete'),
            path('delete/<int:key_log_id>/', views.delete_key_log, name='key_log_delete'),
        ])),
        path('messages/', views.messages_quest, name='quest_messages'),
        path('messages/<int:message_id>/', include([
            path('show/', views.show_message, name='message_show'),
            path('edit/', views.edit_message, name='message_edit'),
            path('delete/', views.delete_message, name='message_delete'),
        ])),
    ])),
]

mission_patterns = [
    path('missions/new/<int:quest_id>/', views.create_mission, name='mission_new'),
    path('missions/<int:mission_id>/', include([
        path('', views.detail_mission, name='mission_detail'),
        path('edit/', views.edit_mission, name='mission_edit'),
        path('delete/', views.delete_mission, name='mission_delete'),
        path('picture/', views.picture_mission, name='mission_picture'),
    ])),
]

hint_patterns = [
    path('hints/<int:hint_id>/', include([
        path('edit/', views.edit_hint, name='hint_edit'),
        path('delete/', views.delete_hint, name='hint_delete'),
    ])),
]

urlpatterns = [
    re_path(r'^', include(quest_patterns)),
    re_path(r'^', include(mission_patterns)),
    re_path(r'^', include(hint_patterns)),
]
