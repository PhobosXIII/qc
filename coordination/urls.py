from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^quests/$', views.all_quests, name='quests'),
    url(r'^quests/(?P<quest_id>[0-9]+)/$', views.detail_quest, name='quest_detail'),
    url(r'^quests/new/$', views.create_quest, name='quest_new'),
    url(r'^quests/(?P<quest_id>[0-9]+)/edit/$', views.edit_quest, name='quest_edit'),
    url(r'^quests/(?P<quest_id>[0-9]+)/delete/$', views.delete_quest, name='quest_delete'),
    url(r'^quests/(?P<quest_id>[0-9]+)/publish/$', views.publish_quest, name='quest_publish'),
]
