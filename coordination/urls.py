from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^quests/$', views.all_quests, name='quests'),
    url(r'^quests/(?P<quest_id>[0-9]+)/$', views.detail_quest, name='quest_detail'),
]
