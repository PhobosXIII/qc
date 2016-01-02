from django.contrib import admin

from main.models import News, HelpCategory, Faq


class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'published_date')


class HelpCategoryAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'title')


class FaqAdmin(admin.ModelAdmin):
    list_display = ('question', 'category')
    list_filter = ('category', )

admin.site.register(News, NewsAdmin)
admin.site.register(HelpCategory, HelpCategoryAdmin)
admin.site.register(Faq, FaqAdmin)
