from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404, redirect

from coordination.models import Quest, Membership
from coordination.permission_utils import is_organizer
from main.models import News, HelpCategory, Faq


def home(request):
    last_news = News.objects.filter(is_published=True)[:3]
    coming_quests = Quest.coming_quests()[:3]
    quest = None
    if request.user.is_authenticated:
        quest = Quest.objects.filter(membership__user=request.user,
                                     membership__role__in=(Membership.PLAYER, Membership.AGENT)).first()
    context = {'coming_quests': coming_quests, 'quest': quest, 'last_news': last_news}
    return render(request, 'home.html', context)


def my_profile(request):
    request = is_organizer(request)
    quest_list = Quest.my_quests(request.user)
    paginator = Paginator(quest_list, 10)
    page = request.GET.get('page')
    try:
        my_quests = paginator.page(page)
    except PageNotAnInteger:
        my_quests = paginator.page(1)
    except EmptyPage:
        my_quests = paginator.page(paginator.num_pages)
    context = {'my_quests': my_quests}
    return render(request, 'registration/my_profile.html', context)


def all_news(request):
    news = News.objects.filter(is_published=True)
    paginator = Paginator(news, 10)
    page = request.GET.get('page')
    try:
        news_list = paginator.page(page)
    except PageNotAnInteger:
        news_list = paginator.page(1)
    except EmptyPage:
        news_list = paginator.page(paginator.num_pages)
    context = {'news_list': news_list}
    return render(request, 'news/all.html', context)


def detail_news(request, news_id):
    news = get_object_or_404(News, pk=news_id)
    context = {'news': news}
    return render(request, 'news/detail.html', context)


def help(request):
    categories = HelpCategory.objects.all()
    if len(categories) > 0:
        category_id = categories.first().pk
        return redirect('help_category', category_id=category_id)
    return render(request, 'help/index.html', {'categories': None})


def help_category(request, category_id):
    category = get_object_or_404(HelpCategory, pk=category_id)
    faqs = Faq.objects.filter(category=category)
    categories = HelpCategory.objects.all()
    context = {'categories': categories, 'faqs': faqs, 'cur_category': category}
    return render(request, 'help/index.html', context)
