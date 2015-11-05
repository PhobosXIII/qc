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
