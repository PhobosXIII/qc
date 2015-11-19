from django.contrib import admin

from main.models import News


class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'published_date')


admin.site.register(News, NewsAdmin)
