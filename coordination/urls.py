from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^quests/$', views.all_quests, name='quests'),
]
