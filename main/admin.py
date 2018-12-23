from django.contrib import admin

from main.models import News, HelpCategory, Faq
from qc.admin import admin_site


class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'published_date')


class HelpCategoryAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'title')


class FaqAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'question', 'category')
    list_filter = ('category',)


admin_site.register(News, NewsAdmin)
admin_site.register(HelpCategory, HelpCategoryAdmin)
admin_site.register(Faq, FaqAdmin)
