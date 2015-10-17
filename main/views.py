from django.shortcuts import render
from django.utils import timezone
from coordination.models import Quest


def home(request):
    now = timezone.now()
    coming_quests = Quest.objects.filter(is_published=True, start__gte=now)[:3]
    context = {'coming_quests': coming_quests}
    return render(request, 'home.html', context)
