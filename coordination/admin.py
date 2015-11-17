from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db import models
from django.forms import SelectMultiple
from coordination.models import Quest, Mission, Hint, CurrentMission, Keylog, Message


def user_str(self):
    if self.first_name:
        return '%s' % self.first_name
    else:
        return '%s' % self.username


User.__str__ = user_str


class MyUserAdmin(UserAdmin):
    list_filter = ()
    list_display = ('username', 'first_name')


class QuestAdmin(admin.ModelAdmin):
    fields = [('title', 'is_published', 'status'), 'organizer', 'start', 'description', 'players']
    list_display = ('title', 'organizer', 'start')
    formfield_overrides = {models.ManyToManyField: {'widget': SelectMultiple(attrs={'size': '10'})}, }
    ordering = ['-start']


class HintInline(admin.TabularInline):
    model = Hint
    extra = 3
    fields = ('order_number', 'text', 'delay')


class MissionAdmin(admin.ModelAdmin):
    fields = ('quest', ('name', 'order_number', 'is_finish'), 'name_in_table', 'text', 'picture', 'key')
    inlines = [HintInline]
    list_display = ('__str__', 'quest', )
    list_filter = ('quest', )
    ordering = ('quest', 'order_number')


class CurrentMissionAdmin(admin.ModelAdmin):
    list_display = ('player', 'get_quest', 'mission', 'start_time')
    ordering = ['-mission', 'start_time']
    list_filter = ('mission__quest', )


class KeylogAdmin(admin.ModelAdmin):
    list_display = ('player', 'get_quest', 'mission', 'key', 'fix_time', 'is_right')
    ordering = ['fix_time']
    list_filter = ('is_right', 'player', 'mission', 'mission__quest')


class MessageAdmin(admin.ModelAdmin):
    list_display = ('text', 'is_show')
    list_filter = ('quest', )


def get_quest(self, obj):
    return obj.mission.quest
get_quest.short_description = 'квест'


CurrentMissionAdmin.get_quest = get_quest
KeylogAdmin.get_quest = get_quest


admin.site.register(Quest, QuestAdmin)
admin.site.register(Mission, MissionAdmin)
admin.site.register(CurrentMission, CurrentMissionAdmin)
admin.site.register(Keylog, KeylogAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
