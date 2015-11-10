from django.conf.urls import url, include
from . import views


quest_patterns = [
    url(r'^quests/$', views.all_quests, name='quests'),
    url(r'^quests/new/$', views.create_quest, name='quest_new'),
    url(r'^quests/(?P<quest_id>[0-9]+)/', include([
        url(r'^$', views.detail_quest, name='quest_detail'),
        url(r'^edit/$', views.edit_quest, name='quest_edit'),
        url(r'^delete/$', views.delete_quest, name='quest_delete'),
        url(r'^publish/$', views.publish_quest, name='quest_publish'),
        url(r'^control/', include([
            url(r'^$', views.control_quest, name='quest_control'),
            url(r'^begin/$', views.begin_quest, name='begin_quest'),
            url(r'^end/$', views.end_quest, name='end_quest'),
            url(r'^clear/$', views.clear_quest, name='clear_quest'),
            url(r'^next_mission/(?P<user_id>[0-9]+)/$', views.next_mission, name='next_mission'),
        ])),
        url(r'^players/', include([
            url(r'^$', views.players_quest, name='quest_players'),
            url(r'^delete/(?P<player_id>[0-9]+)/$', views.delete_player, name='player_delete'),
        ])),
        url(r'^coordination/$', views.coordination_quest, name='quest_coordination'),
        url(r'^tables/$', views.tables_quest, name='quest_tables'),
        url(r'^results/$', views.results_quest, name='quest_results'),
        url(r'^keylog/', include([
            url(r'^$', views.keylog_quest, name='quest_keylog'),
            url(r'^delete/(?P<keylog_id>[0-9]+)/$', views.delete_keylog, name='keylog_delete'),
        ])),
        url(r'^messages/$', views.messages_quest, name='quest_messages'),
        url(r'^messages/(?P<message_id>[0-9]+)/', include([
            url(r'^show/$', views.show_message, name='message_show'),
            url(r'^edit/$', views.edit_message, name='message_edit'),
            url(r'^delete/$', views.delete_message, name='message_delete'),
        ])),
    ])),
]

mission_patterns = [
    url(r'^missions/new/(?P<quest_id>[0-9]+)/$', views.create_mission, name='mission_new'),
    url(r'^missions/(?P<mission_id>[0-9]+)/', include([
        url(r'^$', views.detail_mission, name='mission_detail'),
        url(r'^edit/$', views.edit_mission, name='mission_edit'),
        url(r'^delete/$', views.delete_mission, name='mission_delete'),
    ])),
]

hint_patterns = [
    url(r'^hints/(?P<hint_id>[0-9]+)/', include([
        url(r'^edit/$', views.edit_hint, name='hint_edit'),
        url(r'^delete/$', views.delete_hint, name='hint_delete'),
    ])),
]

urlpatterns = [
    url(r'^', include(quest_patterns)),
    url(r'^', include(mission_patterns)),
    url(r'^', include(hint_patterns)),
]
