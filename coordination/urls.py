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

urlpatterns = [
    url(r'^', include(quest_patterns)),
    url(r'^', include(mission_patterns)),
]
