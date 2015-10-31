from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.forms import SelectMultiple
from coordination.models import Quest, Mission


def user_str(self):
    if self.first_name:
        return '%s' % self.first_name
    else:
        return '%s' % self.username


User.__str__ = user_str


class QuestAdmin(admin.ModelAdmin):
    fields = [('title', 'is_published', 'ended'), 'organizer', 'start', 'description', 'players']
    list_display = ('title', 'organizer', 'start')
    formfield_overrides = {models.ManyToManyField: {'widget': SelectMultiple(attrs={'size': '10'})}, }
    ordering = ['-start']


class MissionAdmin(admin.ModelAdmin):
    fields = ('quest', ('name', 'order_number'), 'name_in_table', 'text', 'picture', 'key')
    list_display = ('__str__', 'quest', )
    list_filter = ('quest', )
    ordering = ('quest', 'order_number')


admin.site.register(Quest, QuestAdmin)
admin.site.register(Mission, MissionAdmin)
